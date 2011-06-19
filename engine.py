import random
from vector2 import *
import sys
import time
import pymongo 
import inspect
from threading import Thread
from scribit import log, logged, timed
import json
from metagrid import MetaGrid, METAGRID_SIZE, GRID_SIZE
from entity import Entity, Updater


TICK_PERIOD = 50 

USE_DATASTORE = False


  


from pymongo.son_manipulator import SONManipulator

class JSONTransformer(SONManipulator):

    def transform_incoming(self, son, collection):


        def get_storage_item(item):

            if isinstance(item, vector2):
                return {"_type" : "vector2", 
                            "vec" :  [item.x, item.y]}
            elif isinstance(item, Entity) or isinstance(item, PersistedWrapper):
                return {"_type" :"ent",
                        "ent_id" : item.id}
            elif isinstance(item, dict):

                return { "_type" : "dict",
                            "pairs" :[ [get_storage_item(key),
                                        get_storage_item(value) ] for 
                                        key, value
                                        in item.items()] }

            return item
 
        for (key, value) in son.items():
            son[str(key)] = get_storage_item(value) 
        return son

    def transform_outgoing(self, son, collection):

        def get_real_item(item):

            if isinstance(item, unicode):
                return str(item)

            if isinstance(item, dict):
                if "_type" in item:
                    if item["_type"] == "vector2":
                         return  vector2(item["vec"][0], 
                                           item["vec"][1])
                    if item["_type"] == "ent":
                         log ('making entity wrapper.')
                         return  PersistedWrapper(item["ent_id"])
 
                    elif item["_type"] == "dict":
                        res = {}
                        for kvp in item["pairs"]:
                            res[get_real_item(kvp[0])]= get_real_item(kvp[1])
                        return res
            
            return item


        for (key, value) in son.items():
                son[str(key)] = get_real_item(value) 
        return son

class ClientManager:
    
    def __init__(self):
        self.clients = {}
        self.to_remove = {}
        
    def add_client(self,client):
        self.clients[client.id] = client

    def remove_client(self,client):
        self.to_remove[client] = True
    
    def update(self):
        for id in self.clients:
            self.clients[id].send_deltas()
        for dude in self.to_remove:
            if dude.id in self.clients:
                del self.clients[dude.id]

       
           

class Engine:
    "The engine controls the whole game, updating entities and shit"
    def __init__(self):
        self.noobs = []
        self.next_id = []
        self.current_frame = 0  
        self.game = None


        if USE_DATASTORE:
            self.mongo_conn = pymongo.Connection()
            self.datastore = self.mongo_conn.snockerball
            self.datastore.add_son_manipulator(JSONTransformer())
        else:
            self.datastore = None

        self.metagrid = MetaGrid(self.datastore)
        self.client_manager = ClientManager() 
        self.ghosts = {}

    def save_world(self, save_terrain=False):


        if not USE_DATASTORE:
            return
        log('saving world..')
            
        for cell in self.metagrid.cells:
            self.metagrid.cells[cell].persist()
            if save_terrain:
                self.metagrid.cells[cell].persist_terrain()
        log ('saving ghosts.')
        for ghost in self.ghosts:
            log ('persisting %s' % self.ghosts[ghost])
            self.ghosts[ghost].persist(self.datastore)
        log ('saving complete.')

    def build_world(self):

        generate = True 
 
        if generate:
            log ('Generating world.')
            if USE_DATASTORE:
                self.datastore.entities.remove()

        for x in range(METAGRID_SIZE):    
            for y in range(METAGRID_SIZE):
               g_x =x*GRID_SIZE
               g_y =y*GRID_SIZE
               #log('new metacell at %d, %d' % (g_x, g_y))
               cell = self.metagrid.add_cell(g_x,g_y)

               if generate and self.game:
                    self.game.new_metagrid_cell(cell)
        if generate:
            if self.game != None:
                self.game.build_world()
            self.save_world(save_terrain=True)
        else: 
           log ('Loading world')
           entities = self.datastore.entities.find() 

           for ent in entities:
               ent_dict = {}
               for var in ent:
                   ent_dict[str(var)] = ent[var]
               guy = entity_class_registry[ent['__class__']](**ent_dict)
           log ('Load complete')


    def add_entity(self, new_guy, moving=False):
        if (hasattr(new_guy, 'pos') and (new_guy.pos)):
            self.metagrid.add_entity(new_guy, moving)
        else:
            if not isinstance(new_guy, Updater):
                log('Why add %s, a ghost that does not update?' 
                            % new_guy)
            self.ghosts[new_guy.id] = new_guy
        

    def remove_entity(self, ent, moving=True):
        if hasattr(ent,'pos') and ent.pos:
            self.metagrid.remove_entity(ent, moving)
        if ent.id in self.ghosts:
            del self.ghosts[ent.id]
 
    def get_entities(self, x, y):
        return self.metagrid.get_entities(x,y)

    def get_entity(self, ent_id):
        if ent_id in self.ghosts:
            return self.ghosts[ent_id]
        return self.metagrid.get_entity(ent_id)

    def make_id(self):
        return ''.join([random.choice(ID_CHARS) for x in range(16)])

    def update(self):
        for id in self.ghosts:
            self.ghosts[id].update()
        self.metagrid.update()
        self.client_manager.update()
      
engine = Engine()



def clamp (min_, x, max_): 
    if x < min_:
        return min_
    elif x > max_:
        return max_
    return x
