import random
from vector2 import *
from engine import *
from entities import *
from scribit import log, logged,timed 
    
class Game:
    "encapsulates the behavior of the entire game"
    
    def __init__(self):
        self.old_score_msg = None
        engine.game = self

    def add_vert_block_line(self,block_class, x, start_y, stop_y):
        for y in xrange(start_y, stop_y+1):
            self.add_block(block_class, vector2(x,y))
        
    def add_horiz_block_line(self, block_class, start_x, stop_x, y):
        for x in xrange(start_x, stop_x + 1):
            self.add_block(block_class,vector2(x,y))
        

    def add_block(self, block_class, pos,solid=True):
        block = block_class(pos)

    def update(self):
        engine.update()

    #@logged    
    def new_metagrid_cell(self, new_cell):
        #add terrain and stuff on it
        choice = 'none'
        for x in range(GRID_SIZE):
            for y in range(GRID_SIZE):
                p = vector2(new_cell.pos[0]+x, new_cell.pos[1]+y)
                #log ('new cell at %s ' % p)
                Terrain(pos=p)
                

    def build_world(self):

        #add some water 
        log ('building world: adding water')
        num_cells = (METAGRID_SIZE*GRID_SIZE)**2
        num_water_cells = int(num_cells*0.05/float(METAGRID_SIZE**2))
        for c in range(num_water_cells):
            x = random.choice(range(GRID_SIZE*METAGRID_SIZE))
            y = random.choice(range(GRID_SIZE*METAGRID_SIZE))

            engine.get_entities(x,y)[LAYER_GROUND].to_water()


        #now add some trees and fruit
        num_bomb_cells =  num_cells*2/(GRID_SIZE*GRID_SIZE)
        log('building world: adding %d bombs' % num_bomb_cells)
        choices =  { 
                         Sheep: GRID_SIZE*0.4,
                         FirePuff : GRID_SIZE*0.4,
                         Coal : GRID_SIZE*0.7,
                         Tree : GRID_SIZE*0.75,
                         Wolf : GRID_SIZE*0.3,
                         Stone: GRID_SIZE*0.3,
                         }

 
        for choice in [Tree] * 4 + \
                      [Coal] * 2 + \
                      [Stone] * 3 + \
                      [Sheep] * 2:
            
            x = random.choice(range(GRID_SIZE*METAGRID_SIZE))
            y = random.choice(range(GRID_SIZE*METAGRID_SIZE))
        

            def get_dudes():
                x = random.choice(range(GRID_SIZE*METAGRID_SIZE))
                y = random.choice(range(GRID_SIZE*METAGRID_SIZE))
                return engine.metagrid.get_entities(x,y)

            dudes = get_dudes() 
            while dudes[LAYER_GROUND].terrain_type == 'water':
                dudes = get_dudes()

            log ('got a dude')
            dudes[LAYER_GROUND].start_forest(choice, choices[choice])

    
