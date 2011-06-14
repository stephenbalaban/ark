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
        for c in range(num_bomb_cells):
            x = random.choice(range(GRID_SIZE*METAGRID_SIZE))
            y = random.choice(range(GRID_SIZE*METAGRID_SIZE))
        
            choices =  { Sheep: GRID_SIZE*0.25,
                         Wolf : GRID_SIZE*0.05,
                         FirePuff : GRID_SIZE*0.1,
                         Fruit : GRID_SIZE*0.125,
                         Tree : GRID_SIZE*0.75}

            choice = random.choice(choices.keys())

            dudes = engine.metagrid.get_entities(x,y)
            if LAYER_GROUND in dudes:
                dudes[LAYER_GROUND].start_forest(choice, choices[choice])

    
