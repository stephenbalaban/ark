import random
from scribit import log
from vector2 import *

GRID_SIZE = 8
METAGRID_SIZE = 8

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
            log ('%s was not in %s' % (ent, self.entities))
            from entity import NoSuchEntity
            import pdb
            pdb.set_trace()
            raise NoSuchEntity('No such entity %s at' % (ent))

class GameGrid:

    def __init__(self, metagrid, size, pos):

        self.cells = {}
        
        for  y in range(size):
            for x in range(size):
                self.cells[(pos[0] +x,pos[1]+y)] = GridCell()
        self.size = size
        self.pos = pos
        self.metagrid = metagrid

    def get_entities(self, x, y):
        x,y = self.metagrid.wrap_coords(x,y)
        return self.cells[(x,y)].get_entities()


    def add_entity(self, ent):
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

    def __init__(self, datastore):
        self.cells = {}
        self.num_cells = METAGRID_SIZE
        self.datastore = datastore

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
            log('cells are: %s ' % self.cells)
            sys.exit()
        else:
            res = self.cells[(g_x, g_y)] 
        
        return res

    def add_entity(self, new_guy,moving=False): 
            self.get_cell(new_guy.pos.x, 
                        new_guy.pos.y).add_entity(new_guy,moving) 

    def get_entity(self, ent_id):
        for cell_pos in self.cells:
            res = self.cells[cell_pos].get_entity(ent_id)
            if res:
                return res
        return None

    def add_cell(self, g_x, g_y):
        res =  MetaGridCell(self, (g_x,g_y),self.datastore)
        self.cells[(g_x,g_y)]  = res
        return res
       
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


        closest = []
        def circle_visitor(x,y):
            dudes = self.get_entities(x,y)
            if layer in dudes:
                if selector(dudes[layer]):
                    closest.append(dudes[layer])
   
        for r in range(max_dist+1):
            self.visit_circle(x,y, r, circle_visitor)

        if closest:
            return closest[0]

    def visit_circle(self, cx,cy, radius, visitor):
        f = 1 - radius
        ddF_x = 1
        ddF_y = -2*radius
        x = 0
        y = radius

        visitor(cx,cy+radius)
        visitor(cx,cy-radius)
        visitor(cx+radius, cy)
        visitor(cx-radius, cy)


        while x < y:
            if f >= 0:
                y-=1
                ddF_y += 2
                f += ddF_y

            x += 1
            ddF_x += 2
            f += ddF_x

            visitor(cx+x, cy+y)
            visitor(cx-x, cy+y)
            visitor(cx+x, cy-y)
            visitor(cx-x, cy-y)
            visitor(cx+y, cy+x)
            visitor(cx-y, cy+x)
            visitor(cx+y, cy-x)
            visitor(cx-y, cy-x)


class MetaGridCell:
        """encapsulates the behavior of the entire game"""
        def __init__(self,metagrid, pos, datastore):
                self.dude_map = {}
                self.noobs = {} 
                self.deads = {}
                self.moved_away = {}
                self.moved_here = {}
                self.pos = pos
                self.grid = GameGrid(metagrid, GRID_SIZE, pos)
                self.current_frame = 0
                self.current_state = None
                self.last_delta = None
                self.updaters = {} 
                self.drop_message = {}
                self.datastore = datastore
                self.metagrid = metagrid

    
        def get_pos(self):
            return vector2(self.pos[0],
                           self.pos[1])
        def __repr__(self):
            return "MetaGridCell at %d,%d." % self.pos                


        def add_entity(self, entity, moving= False):

            if hasattr(entity,'id'):
                if entity.id in self.deads:
                    del self.deads[entity.id]
                    self.grid.add_entity(entity)
                    return
            if moving:
                self.moved_here[entity] = True
            else:
                self.noobs[entity.id] = entity
            if hasattr(entity, 'pos') and entity.pos:
                self.grid.add_entity(entity)

        def remove_entity(self, entity, moving=False):
            #don't put this guy on the list of dead entities
            #if he's just moving to another location
            if hasattr(entity, 'pos') and entity.pos:
                self.grid.remove_entity(entity)
 
            if entity.id in self.noobs:
                del self.noobs[entity.id]
                return

            if not moving:
                self.deads[entity.id] = entity
            else:
                self.moved_away[entity.id] = entity
               
        def get_entity(self, ent_id):
            if ent_id in self.dude_map:
                return self.dude_map[ent_id]
            if ent_id in self.noobs:
                return self.noobs[ent_id]
            return None

        def get_free_position(self, layer):
            return self.grid.get_free_position(layer)

        def _add_noobs(self):

                from entity import Updater
                noob_count = len(self.noobs)
                mover_count = len(self.moved_here)
                if noob_count + mover_count:
                    msg = "%s adding %d noobs and %d movers."
                    msg = msg % (self, noob_count, mover_count)
                    #log(msg)
                noob_map = {}

                for noob_id in self.noobs:
                    noob = self.noobs[noob_id]
                    self.dude_map[noob_id] = noob
                    noob_map[noob_id] = noob.get_state()

                    if isinstance(noob, Updater):
                        #log("%s Adding noob %s." % (self, noob))
                        self.updaters[noob] = True

                for mover in self.moved_here:
                    self.dude_map[mover.id] = mover
                    if isinstance(mover, Updater):
                        #log ("%s Adding mover %s." % (self, mover))
                        self.updaters[mover] = True

                self.moved_here = {} 
                self.noobs = {} 
                return noob_map


        def _get_entities_in_radius(self, pos, radius):

                results = []
                for id in self.dude_map:
                        ent = self.dude_map[id]
                        delta = (ent.pos - pos).length()
                        if delta < ent.size.length() + radius:
                                results += [ent]
                return results


        def persist_terrain(self):
            for ent_id in self.dude_map:
                ent = self.dude_map[ent_id]
                ent.persist(self.datastore)
            for ent in self.noobs:
                ent.persist(self.datastore)

        def persist(self):
            for entity in self.updaters:
                entity.persist(self.datastore)
    


        def _update_entity_map(self):
                # prune out the dead entities by building a new entity map
                
            from entity import Updater
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
                            #log ("Deleting updater %s." % entity)
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
                if not entity.dead:
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


