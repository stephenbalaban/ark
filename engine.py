import random
from vector2 import *
import sys
import time

from scribit import log, logged, timed

TICK_PERIOD = 50 
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
METAGRID_SIZE = 8
ID_CHARS = [chr(x) for x in range(256) 
                if (chr(x).isalpha() or chr(x).isdigit())]

class ClientManager:
    
    def __init__(self):
        self.clients = {}
        
    def add_client(self,client):
        self.clients[client.id] = client
    
    def update(self):
        for id in self.clients:
            self.clients[id].update()

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
            raise NoSuchEntity('No such entity %s')

class GameGrid:

    def __init__(self, size, pos):

        self.cells = {}
        
        for  y in range(size):
            for x in range(size):
                self.cells[(pos[0] +x,pos[1]+y)] = GridCell()
        self.size = size
        self.pos = pos

    def get_entities(self, x, y):
        x,y = engine.metagrid.wrap_coords(x,y)
        return self.cells[(x,y)].get_entities()


    def add_entity(self, ent):
        log ('cell at %d, %d, adding entity' % self.pos)
        return self.cells[(ent.pos.x,ent.pos.y)].add_entity(ent)

    def remove_entity(self, ent):
        cell =  self.cells[(ent.pos.x, ent.pos.y)]
        return cell.remove_entity(ent)


    #@timed
    def get_free_position(self, layer, tries=10):
        "GameGrid at %s getting free position for layer %s" % (self.pos, layer)
        placed = False
        
        while not placed and tries:
            tries = tries - 1
            x = self.pos[0] + random.randint(0, GRID_SIZE-1)
            y = self.pos[1] + random.randint(0, GRID_SIZE-1)
            if not layer in self.get_entities(x,y):
                return vector2(x,y)

class MetaGrid:

    def __init__(self):
        self.cells = {}
        self.num_cells = METAGRID_SIZE

    def wrap_coords(self, x,y):
        x = x % (METAGRID_SIZE*GRID_SIZE)
        y = y % (METAGRID_SIZE*GRID_SIZE)
        return x,y
       
    def get_cell(self, x, y):
        x,y = self.wrap_coords(x,y)
        g_x = (x / GRID_SIZE)*GRID_SIZE
        g_y = (y / GRID_SIZE)*GRID_SIZE

        #log("%d,%d converted to %d,%d" % (x,y, g_x, g_y))
        if not (g_x,g_y) in self.cells:
            log("FATAL: unknown metagrid cell %d,%d" % (g_x, g_y))
            sys.exit()
        else:
            res = self.cells[(g_x, g_y)] 
        
        return res

    def add_entity(self, new_guy,moving=False): 
        self.get_cell(new_guy.pos.x, 
                        new_guy.pos.y).add_entity(new_guy,moving) 

    def add_cell(self, g_x, g_y):
      self.cells[(g_x,g_y)] = res =  MetaGridCell((g_x,g_y))
      engine.game.new_metagrid_cell(res) 
       
    def remove_entity(self, dead_guy, moving=False):
        x,y = self.wrap_coords(dead_guy.pos.x,dead_guy.pos.y)
        cell = self.get_cell(x, y)
        cell.remove_entity(dead_guy, moving)

   # @logged
    def move_entity(self, mover, new_pos):
        cell = self.get_cell(mover.pos.x, mover.pos.y)
        cell.remove_entity(mover, moving=True)
        mover.pos = new_pos
        self.get_cell(new_pos.x, new_pos.y).add_entity(mover, moving=True)
        
    def get_entities(self, x, y):
        x,y = self.wrap_coords(x,y)
        return self.get_cell(x,y).grid.get_entities(x,y)

    def get_neighbors(self, pos):
        neighbors = {}

        neighbors[LEFT] = self.get_entities(pos.x-1, pos.y)
        neighbors[RIGHT] = self.get_entities(pos.x+1, pos.y)
        neighbors[UP] = self.get_entities(pos.x, pos.y-1)
        neighbors[DOWN] =self.get_entities(pos.x, pos.y+1)  
        neighbors[UP_LEFT] = self.get_entities(pos.x-1, pos.y-1)
        neighbors[UP_RIGHT] = self.get_entities(pos.x+1, pos.y-1)
        neighbors[DOWN_LEFT] = self.get_entities(pos.x-1, pos.y+1)
        neighbors[DOWN_RIGHT] =self.get_entities(pos.x+1, pos.y+1)  


        return neighbors

    def get_free_position(self, layer, tries=10):
        keys = [k for k in self.cells]
        if len(keys) == 0:
            return self.get_cell(0,0).get_free_position(layer)
        return self.cells[random.choice(keys)].get_free_position(layer)

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
        self.client_manager = ClientManager() 

    def build_world(self):
        for x in range(METAGRID_SIZE):    
            for y in range(METAGRID_SIZE):
               g_x =x*GRID_SIZE
               g_y =y*GRID_SIZE
               log('new metacell at %d, %d' % (g_x, g_y))
               self.metagrid.add_cell(g_x,g_y)
        self.game.build_world()
                  

    def add_entity(self, new_guy, moving=False):
        self.metagrid.add_entity(new_guy, moving)
        
    def add_client(self, client):
        self.client_manager.add_client(client)

    def remove_entity(self, ent, moving=True):
        self.metagrid.remove_entity(ent, moving)
 
    def get_entities(self, x, y):
        return self.metagrid.get_entities(x,y)

    def make_id(self):
        return ''.join([random.choice(ID_CHARS) for x in range(32)])

    def update(self):
        self.metagrid.update()
        self.client_manager.update() 

class MetaGridCell:
        """encapsulates the behavior of the entire game"""
        def __init__(self,pos):
                self.dude_map = {}
                self.noobs = []
                self.deads = {}
                self.moved_away = {}
                self.moved_here = {}
                self.pos = pos
                self.grid = GameGrid(GRID_SIZE, pos)
                self.current_frame = 0
                self.current_state = None
                self.last_delta = None
                self.updaters = {} 
                self.drop_message = {}
    
        def __repr__(self):
            return "MetaGridCell at %d,%d." % self.pos                


        def add_entity(self, entity, moving= False):

            if hasattr(entity,'id'):
                if entity.id in self.deads:
                    del self.deads[entity.id]
                    self.grid.add_entity(entity)
                    return
            else:
                entity.id = engine.make_id()
            if moving:
                self.moved_here[entity] = True
            else:
                self.noobs += [entity]
            self.grid.add_entity(entity)

        def make_entity_id(self):
            return ''.join([random.choice('0123456789abcedfeABCDEF') 
                            for x in range(32)])
    
        def remove_entity(self, entity, moving=False):
            #don't put this guy on the list of dead entities
            #if he's just moving to another location
            if not moving:
                self.deads[entity.id] = entity
            else:
                self.moved_away[entity.id] = entity
            self.grid.remove_entity(entity)
                

        def get_free_position(self, layer):
            return self.grid.get_free_position(layer)

        def _add_noobs(self):
                noob_count = len(self.noobs)
                mover_count = len(self.moved_here)
                if noob_count + mover_count:
                    msg = "%s adding %d noobs and %d movers."
                    msg = msg % (self, noob_count, mover_count)
                    #log(msg)
                noob_map = {}

                for noob in self.noobs:
                    self.dude_map[noob.id] = noob
                    noob_map[noob.id] = noob.get_state()
                    if isinstance(noob, Updater):
                        log("%s Adding noob %s." % (self, noob))
                        self.updaters[noob] = True

                for mover in self.moved_here:
                    self.dude_map[mover.id] = mover
                    if isinstance(mover, Updater):
                        log ("%s Adding mover %s." % (self, mover))
                        self.updaters[mover] = True

                self.moved_here = {} 
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
                        dead = entity.id in self.deads
                        moved = entity.id in self.moved_away
                        if (entity and not\
                            dead and not moved):                     
                            new_map[id] = entity
                        if dead:
                            deads += [id]
                        if dead or moved:
                            if isinstance(entity,Updater):
                                log ("Deleting updater %s." % entity)
                                del self.updaters[entity]
                self.dude_map = new_map
                noobs = self._add_noobs()
                self.current_frame += 1
                self.deads = {}
                self.moved_away = {}
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
            drop_message = {'type' : 'drop',
                            'ents' : []} 
            
            for entity in self.updaters:
                entity.update()

            for ent_id in self.dude_map:
                entity = self.dude_map[ent_id]
                if entity:
                    delta = entity.get_delta()
                    if len(delta):
                        delta_list['deltas'][entity.id] = delta
                    gamestate['ents'][entity.id] = entity.get_state()
                    drop_message['ents'] += [entity.id]
                            
            self.current_state = { 'type' : 'gs',
                                   'state' : gamestate,
                                'frame' : self.current_frame }

            self.drop_message = drop_message
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


    def __repr__(self):
        return "%s at %d, %d" % (self.__class__.__name__,
                                 self.pos.x,
                                 self.pos.y)

    def __setattr__(self, attr_name, value):

        if attr_name in self.net_vars:
            if attr_name in self.__dict__:
                if self.__dict__[attr_name] == value:
                    return 
            self.delta[attr_name] = value
        self.__dict__[attr_name] =  value

    def move(self, new_pos):
        x,y = engine.metagrid.wrap_coords(new_pos.x, new_pos.y)
        new_pos = vector2(x,y)
        engine.metagrid.move_entity(self,new_pos)
    
    def update(self):
        pass 
      
    
    def change_tex(self, new_tex):
        self.tex = new_tex

    def change_size(self, new_size):
        self.size  = new_size

    def die(self, killer=None):
        engine.remove_entity(self,moving=False)
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
                
class NoSuchEntity: pass
class Updater: pass

def clamp (min_, x, max_): 
    if x < min_:
        return min_
    elif x > max_:
        return max_
    return x
