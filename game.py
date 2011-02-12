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

    def make_maze(self):

        #make the boundaries
        walls =False 
        add_road=False;
        
        forest_size = 4
    
        
        if walls:
            self.add_horiz_block_line(SolidBlock, 0, GRID_SIZE - 1, GRID_SIZE - 1)
            self.add_horiz_block_line(SolidBlock, 0, GRID_SIZE -1, 0)
            self.add_vert_block_line(SolidBlock, 0, 1, GRID_SIZE - 2)
            self.add_vert_block_line(SolidBlock, GRID_SIZE-1, 1, GRID_SIZE -2)
        
        def vert_road_adder(pos):
            Road(pos, True)
            return

        def horiz_road_adder(pos):
            Road(pos, False)
            
        #self.add_horiz_block_line(horiz_road_adder, 1, GRID_SIZE-2, GRID_SIZE/2)
        return 
        for x in range(GRID_SIZE):
            for y in range(GRID_SIZE):
                try:
                    Terrain(vector2(x,y))
                except:
                    pass
       
        
        #FruitPatch(2,2,GRID_SIZE-4,GRID_SIZE-4)
        #Forest(2,2, GRID_SIZE-4, GRID_SIZE-4)
        #for x in range(5):
        #    Alien(None) 
        
        #Flag(engine.grid.get_free_allmostposition(LAYER_BLOCKS), "red")
        #Flag(engine.grid.get_free_position(LAYER_BLOCKS),"blue")
        #Lake(19,2,6,6) 
        #Building(25,2,4,4)

        #Building(19,8,4,4)
        #Building(25,8,4,4)

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
        #add terrain
        choices = {'none' : 1.0,
                    'water' : 0.95,
                    'trees' : 0.8,
                    'fruit' : 0.25}
        #choice = random.choice(choices.keys())
        choice = 'none'
        for x in range(GRID_SIZE):
            for y in range(GRID_SIZE):
                p = vector2(new_cell.pos[0]+x, new_cell.pos[1]+y)
                t = Terrain(p)
                if random.random() < choices[choice]:
                    if choice == 'water' :
                        t.to_water() 
                    elif choice == 'trees' :
                        Tree(p)
                    elif choice == 'fruit':
                        Fruit(p)
                    
        #now put stuff on this terrain

        
