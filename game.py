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

        if walls:
            self.add_horiz_block_line(SolidBlock, 0, GRID_SIZE -1, GRID_SIZE - 1)
            self.add_horiz_block_line(SolidBlock, 0, GRID_SIZE -1, 0)

            self.add_vert_block_line(SolidBlock, 0, 0, GRID_SIZE - 1)
            self.add_vert_block_line(SolidBlock, GRID_SIZE-1, 0, GRID_SIZE -1)

        self.add_horiz_block_line(RedBlock, 4, GRID_SIZE - 4, 4)
        self.add_horiz_block_line(BlueBlock, 4, GRID_SIZE - 4, GRID_SIZE -4)
        #add the initial diamond
        Snockerball(vector2(GRID_SIZE/2, GRID_SIZE/2))
        
        boost_start = 3*GRID_SIZE/8
        boost_stop = 5*GRID_SIZE/8
        for i in range(boost_start, boost_stop):
            Booster(vector2(boost_stop, i), RIGHT)
            Booster(vector2(boost_start, i), LEFT)
            Booster(vector2(i, boost_stop), DOWN)
            Booster(vector2(i, boost_start ), UP)


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
            
