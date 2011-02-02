import random
from vector2 import *
from engine import *
from entities import *

    
class Game:
    "encapsulates the behavior of the entire game"
    
    def __init__(self):
        self.old_score_msg = None


    def make_maze(self):

        #make the boundaries
        walls = True
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

        for x in range(GRID_SIZE):
            for y in range(GRID_SIZE):
                try:
                    Terrain(vector2(x,y))
                except:
                    pass
       
        
        FruitPatch(2,2,GRID_SIZE-4,GRID_SIZE-4)
        Forest(2,2, GRID_SIZE-4, GRID_SIZE-4)
        for x in range(5):
            Alien(None) 
        
        #Flag(engine.grid.get_free_position(LAYER_BLOCKS), "red")
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
        
        score_msg = self.get_score_msg()
        if score_msg != self.old_score_msg:
            #print score_msg
            engine.client_manager.broadcast(score_msg)
            self.old_score_msg = score_msg


    def get_score_msg(self):
        scores = []
        for client_id in engine.client_manager.clients:
            client = engine.client_manager.clients[client_id]
            scores += [{'player' : client.name,
                        'kills' : client.kill_count}]
        return {'type' :  'score',
                'scores' : scores}
            
