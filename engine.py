import random
from vector2 import *
import time

from scribit import log, logged, timed

TICK_PERIOD = 250
UP = vector2(0,-1)
DOWN = vector2(0,1)
LEFT = vector2(-1,0)
RIGHT = vector2(1,0)

DIR_NAMES = {UP: 'up', DOWN : 'down', LEFT : 'left', RIGHT : 'right'}
DIR_OPPOSITES = {UP : DOWN, DOWN: UP, LEFT : RIGHT, RIGHT : LEFT}
ORDINALS = [UP, DOWN, LEFT, RIGHT]
UP_LEFT= UP+LEFT
UP_RIGHT= UP+RIGHT
DOWN_LEFT = DOWN+LEFT
DOWN_RIGHT = DOWN+RIGHT
DIAGONALS = [UP_LEFT, UP_RIGHT, DOWN_LEFT, DOWN_RIGHT]
ALL_DIRS = DIAGONALS + ORDINALS
ENTITY_SIZE = vector2(8,8)
GRID_SIZE = 8 
ID_CHARS = [chr(x) for x in range(256) 
                if (chr(x).isalpha() or chr(x).isdigit())]

class ClientManager:
    
    def __init__(self):
        self.clients = {}
        self.next_client_id = 0
        
    def add_client(self,client):
        self.next_client_id += 1;
        self.clients[self.next_client_id] = client
        client.id = self.next_client_id
              
    def broadcast(self, message):
        #some clients have disconnected
        #keep track of this
        new_clients = {}                                       
        for id in self.clients:
            try:            
                self.clients[id].send(message)
                new_clients[id] = self.clients[id]
            except IOError, e:
                print "client",id,"disconnected."
                self.clients[id].disconnect()
        self.clients = new_clients

class CellFull(Exception): pass
class GridCell:
        
        def __init__(self):

            self.entities = {}

        def get_entities(self):
                ents = {}
                for layer in self.entities:
                        ent = self.entities[layer]
                        ents[layer] = ent
                return ents

        def add_entity(self, ent):
            "Tries to add the entity. Returns false if "\
            "that layer is full."
            if ent.layer in self.entities:
                    raise CellFull("couldn't add %s at %d, %d ,%d"\
                                            ", a %s was there" % (ent, 
    ent.pos.x, ent.pos.y, ent.layer, self.entities[ent.layer]))
            self.entities[ent.layer] = ent
            return True

        def remove_entity(self, ent):

            if ent.layer in self.entities:
                    other = self.entities.pop(ent.layer)
                    return True
            else:
                    return False    

class GameGrid:

    def __init__(self, size, pos):

        self.cells = {}
        
        for  y in range(size):
            for x in range(size):
                self.cells[(pos[0] +x,pos[1]+y)] = GridCell()

        self.size = size
        self.pos = pos

    def get_entities(self, x, y):
        return self.cells[(x,y)].get_entities()


    def add_entity(self, ent):
        return self.cells[(ent.pos.x,ent.pos.y)].add_entity(ent)

    def remove_entity(self, ent):
        key = (ent.pos.x, ent.pos.y)
        if not key in self.cells:
            import pdb
            pdb.set_trace()
        return self.cells[(ent.pos.x, ent.pos.y)].remove_entity(ent)


    @timed
    def get_free_position(self, layer, tries=10):
        "GameGrid at %s getting free position for layer %s" % (self.pos, layer)
        placed = False
        
        while not placed and tries:
            tries = tries - 1
            x = random.randint(0, GRID_SIZE-1)
            y = random.randint(0, GRID_SIZE-1)
            if not layer in self.get_entities(x,y):
                return vector2(x,y)
        return None

class MetaGrid:

    def __init__(self):
        self.cells = {}
           
    def get_cell(self, x, y):
        g_x = x - (x%GRID_SIZE)
        g_y = y - (y%GRID_SIZE)

        if not (g_x,g_y) in self.cells:
            log ('Spawning a cell at %d, %d' % (g_x,g_y))
            self.cells[(g_x,g_y)] = MetaGridCell((g_x,g_y))
        return self.cells[(g_x, g_y)] 

    def add_entity(self, new_guy): 
        self.get_cell(new_guy.pos.x, new_guy.pos.y).add_entity(new_guy) 

    def remove_entity(self, dead_guy):
        self.get_cell(dead_guy.pos.x, dead_guy.pos.y).remove_entity(dead_guy)

    @logged
    def move_entity(self, mover, new_pos):
        self.get_cell(mover.pos.x, mover.pos.y).remove_entity(mover)
        mover.pos = new_pos
        self.get_cell(new_pos.x, new_pos.y).add_entity(mover)
        
    def get_entities(self, x, y):
        return self.get_cell(x,y).grid.get_entities(x,y)

    def get_neighbors(self, pos):
        neighbors = {}

        neighbors[LEFT] = self.get_entities(pos.x-1, pos.y)
        neighbors[RIGHT] = self.get_entities(pos.x+1, pos.y)
        neighbors[UP] = self.get_entities(pos.x, pos.y-1)
        neighbors[DOWN] =self.get_entities(pos.x, pos.y+1)  

        return neighbors

    def get_free_position(self, layer, tries=10):
        keys = [k for k in self.cells]
        if len(keys) == 0:
            return self.get_cell(0,0).get_free_position(layer)
        return self.cells[random.choice(keys)].get_free_position(layer)

    def add_client(self, client):
        self.get_cell(client.dude.pos.x,
                      client.dude.pos.y).add_client(client)
    def update(self):
        keys = [k for k in self.cells]
        random.shuffle(keys)
        for key in keys:
            self.cells[key].update()
                    

    def find_nearest(self, x, y, layer, max_dist=4, selector = lambda ent : True):
        for i in range(max_dist):
            for j in range(max_dist):
                this_x = x + i - max_dist/2
                this_y = y + j - max_dist/2
                dudes = self.get_entities(this_x,this_y)
                if layer in dudes:
                    if selector(dudes[layer]):
                        return dudes[layer]


class Engine:
    "The engine controls the whole game, updating entities and shit"
    def __init__(self):
        self.noobs = []
        self.next_id = []
        self.current_frame = 0  
        self.metagrid = MetaGrid()
        

    def add_entity(self, new_guy):
        self.metagrid.add_entity(new_guy)
        
    def add_client(self, client):
        self.metagrid.get_cell(client.dude.pos.x,
                                client.dude.pos.y).add_client(client)

    def remove_entity(self, ent):
        self.metagrid.remove_entity(ent)
 
    def get_entities(self, x, y):
        return self.metagrid.get_entities(x,y)

    def make_id(self):
        return ''.join([random.choice(ID_CHARS) for x in range(32)])

    @timed
    def update(self):
        self.metagrid.update()
        

class MetaGridCell:
        """encapsulates the behavior of the entire game"""
        def __init__(self,pos):
                self.client_manager = ClientManager()        
                self.dude_map = {}
                self.noobs = []
                self.deads = {}
                self.pos = pos
                self.grid = GameGrid(GRID_SIZE, pos)
                self.current_frame = 0
                self.current_state = None
                self.last_delta = None
                self.updaters = {} 
    
        def __repr__(self):
            return "MetaGridCell at %d,%d." % self.pos                

        def add_client(self, client):
                #add this guy to the list of clients
                self.client_manager.add_client(client)
                #client.send(self.current_state)


        def add_entity(self, entity):

            if hasattr(entity,'id'):
                if entity.id in self.deads:
                    del self.deads[entity.id]
                    self.grid.add_entity(entity)
                    return
            else:
                entity.id = engine.make_id()
            self.noobs += [entity]
            self.grid.add_entity(entity)

        def make_entity_id(self):
            return ''.join([random.choice('0123456789abcedfeABCDEF') 
                            for x in range(32)])
    
        def remove_entity(self, entity):
                self.deads[entity.id] = entity
                self.grid.remove_entity(entity)
                

        def get_free_position(self, layer):
            return self.grid.get_free_position(layer)

        def _add_noobs(self):
                if len(self.noobs):
                    log ("Adding %d noobs." % len(self.noobs))
                noob_map = {}
                for noob in self.noobs:
                        self.dude_map[noob.id] = noob
                        noob_map[noob.id] = noob.get_state()
                        if isinstance(noob, Updater):
                            self.updaters[noob] = True
                self.noobs = []
                return noob_map


        def _get_entities_in_radius(self, pos, radius):

                results = []
                for id in self.dude_map:
                        ent = self.dude_map[id]
                        delta = (ent.pos - pos).length()
                        if delta < ent.size.length() + radius:
                                results += [ent]
                return results



        def _update_entity_map(self):
                # prune out the dead entities by building a new entity map
                
                deads = []
                new_map = {}
                for id in self.dude_map:
                        entity = self.dude_map[id]
                        if (entity and not entity.id in self.deads):
                            new_map[id] = entity
                        else:
                            deads += [id]
                            if isinstance(entity,Updater):
                                del self.updaters[self.deads[id]]
                self.dude_map = new_map
                noobs = self._add_noobs()
                self.current_frame += 1
                self.deads = {}
                return noobs, deads

                          
                
        def update(self):
            noobs, deads = self._update_entity_map()
            delta_list = {'type' : 'delta',
              'noobs' : noobs,
              'deads' : deads, 
              'deltas': {},      
              'frame' : self.current_frame}
            gamestate = { 'type' : 'gs',
                                      'ents' : {}}
            for client_id in self.client_manager.clients:
                client = self.client_manager.clients[client_id]
                client.update()

            for entity in self.updaters:
                entity.update()

            for ent_id in self.dude_map:
                entity = self.dude_map[ent_id]
                if entity:
                    delta = entity.get_delta()
                    if len(delta):
                        delta_list['deltas'][entity.id] = delta
                    gamestate['ents'][entity.id] = entity.get_state()
                            
            self.current_state = { 'type' : 'gs',
                   'state' : gamestate,
                'frame' : self.current_frame }
            
            #tell everyone about the current gamestate
            #but don't bother if there are no changes
            self.last_delta = delta_list


engine = Engine()



class Entity:
    "abstract base class for things in the game"
    def __init__(self, pos, size, layer=0):

        self.__dict__['net_vars'] = {
                 'tex': True,
                 'angle' : True,
                 'size' :True,
                 'pos' : True,
                  'layer' : True,
                 'height': 0,
                 'id' : -1,
                 'lerp_targets' : {},
                 'lerp_frames' : {},
                 'frame' : 0
                }           


        self.__dict__["delta"] = {}
        
    
            
        self.tex = 'none.png'
        self.dead = False
        self.pos = pos
        self.size = size
        self.dir = ZERO_VECTOR
        self.angle = 0
        self.layer = layer 
        self.height = 0
        self.lerp_targets = {}
        self.lerp_frames = {}
        self.frame = 0
        engine.add_entity(self)

    def __setattr__(self, attr_name, value):

        if attr_name in self.net_vars:
            if attr_name in self.__dict__:
                if self.__dict__[attr_name] == value:
                    return 
            self.delta[attr_name] = value
        self.__dict__[attr_name] =  value

    def move(self, new_pos):
        engine.metagrid.move_entity(self,new_pos)
    
    def update(self):
        pass 
        
    def change_tex(self, new_tex):
        self.tex = new_tex

    def change_size(self, new_size):
        self.size  = new_size

    def die(self, killer=None):
        engine.remove_entity(self)
        self.dead = True

    def get_state(self):

        state = {}
        for varname in self.net_vars:
            val = self.__dict__[varname]
            if hasattr(val, 'to_json'):
                val = val.to_json()
            state[varname] = val
        return state

    def get_delta(self):
        out_delta = {}
        #do json encoding here
        for varname in self.delta:
            val = self.delta[varname]
            if hasattr(val,'to_json'):
                val = val.to_json()
            out_delta[varname] = val
        self.delta = {}
        return out_delta
                
class Updater: pass

def clamp (min_, x, max_): 
    if x < min_:
        return min_
    elif x > max_:
        return max_
    return x
