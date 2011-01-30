from random import *
from vector2 import *
from engine import *


from random import *
from vector2 import *
from engine import *




LAYER_GROUND = 0
LAYER_BLOCKS = 1
LAYER_POWERUPS = 2


ACT_PLACE = 1
class Mover(Entity):

    def try_move(self, push_dir):

        if not (push_dir.x == 0  and push_dir.y == 0):
            target = self.pos + push_dir;
            other_target = target+push_dir;

            ents = engine.grid.get_entities(target.x,
                                            target.y)

            other_ents = engine.grid.get_entities(other_target.x,
                                                   other_target.y)
            blocked = False
            if  self.layer in ents:
                #see if this guy to the right can move
                other = ents[self.layer] 
                if isinstance(other, Mover):
                    if self.can_push(other) and other.try_move(push_dir):
                        other.take_push(self, other_target)
                        self.push(other)
                    elif self.can_smash(other):
                        other.take_smash(self)
                        self.smash(other)
                    else:
                        blocked = True
                        
            if not blocked:  
                self.move(target)
            return not blocked

        return True

    def touch(self, other):
        pass
    def can_push(self,  other):
        return False
    def can_smash(self, other):
        return False
    def push(self, victim):
        pass
    def smash(self, victim):
        pass
            
    def take_push(self, pusher, target):
        self.move(target)
    def take_smash(self,  smasher):
        self.die()

class Carryable(Entity):

    def __init__(self, pos):
        Entity.__init__(self, pos, ENTITY_SIZE, LAYER_BLOCKS)
        self.type = random.choice(['lemon',
                                  'cherry'])
        self.tex = "carried\\%s.png" % self.type
        self.height = ENTITY_SIZE.x
        self.carried_by = None
    def update(self):
        if self.carried_by:
            self.pos = self.carried_by.pos
class Dude(Mover):

    def __init__(self,owner):

        pos = engine.grid.get_free_position(LAYER_BLOCKS)

        Entity.__init__(self, pos, vector2(8,16), LAYER_BLOCKS )

        self.net_vars['anim'] = True

        self.act = None
        self.owner = owner
        self.solid = True
        self.dir = ZERO_VECTOR
        self.last_dir = RIGHT
        self.act = None
        self.on_die = None
        self.frames = 2
        self.team = random.choice(['blue','red'])
        self.tex = 'warrior_right'        
        self.anim = 'dude'
        self.walking = False
        #states are: standing, moving, acting
        self.state = 'standing'
        self.carrying = None

    def push(self, pushee):
        pass
 
    def get_delta(self):
        delta = Entity.get_delta(self)
        return delta 
    def can_push(self,other):
        can =  isinstance(other, WoodPile)
        can = can or isinstance(other, Flag)

        return can


    def update(self):
        if not self.dir.is_zero():
            if self.dir == self.last_dir:
                self.state = 'moving'
                self.try_move(self.dir)
            self.last_dir = self.dir
        elif self.act == 'use':
            self.state = 'using'
            self.use()
        else:
            self.state = 'standing'
        self.update_texture()
         

    def use(self):
        

        if self.carrying:
            
            self.carrying.pos = self.pos + self.last_dir
            try:
                engine.grid.add_entity(self.carrying)
                self.carrying.carried_by = None
                self.carrying.height = ENTITY_SIZE.x
                self.carrying = None
            except CellFull:
                self.carrying.pos = self.pos
            return
       
       
        #check for an item to act on
        neighbors = engine.grid.get_neighbors(self.pos)
        if self.last_dir in neighbors:
            dudes = neighbors[self.last_dir]
            if LAYER_BLOCKS in dudes:
                other_guy = dudes[LAYER_BLOCKS]
                if isinstance(other_guy, Tree):
                    other_guy.die()
                    Carryable(other_guy.pos())
                elif isinstance(other_guy, Carryable):
                    other_guy.carried_by = self
                    #he doesn't count in the grid any more
                    engine.grid.remove_entity(other_guy)
                    other_guy.height = ENTITY_SIZE.x*4
                    self.carrying = other_guy
            else:
                PlowedPatch(self.pos+self.last_dir)


    def update_texture(self):
        if self.state == 'using':
            self.tex = 'warrior/action/'+DIR_NAMES[self.last_dir]+'/'
            return
       
        else:
            self.tex = 'warrior/walk/'+DIR_NAMES[self.last_dir]+'/'

            return



    def die(self, killer):
        if self.on_die:
            self.on_die()
        killer.on_kill(self)
        Entity.die(self)
                
class Background(Entity):
    
    def __init__(self, pos):
        Entity.__init__(self,pos,  ENTITY_SIZE,LAYER_GROUND)

        self.tex = 'grass.png' 

class Road(Entity):

    def __init__(self, pos, is_vertical):
        Entity.__init__(self, pos, ENTITY_SIZE, LAYER_GROUND)
        if is_vertical:
                        self.tex = 'road_vertical.png'
        else:
                        self.tex = 'road_horizontal.png'

class PlowedPatch(Mover):
    def __init__(self, pos):
        Entity.__init__(self, pos, ENTITY_SIZE, LAYER_BLOCKS)
        self.tex = 'plowed.png'

class Tree(Mover):
    def __init__(self, pos):
        Entity.__init__(self, pos, vector2(8,16), LAYER_BLOCKS)
        self.tex = 'full_tree.png'
        self.height = ENTITY_SIZE.x*2

class WoodPile(Mover, Carryable):
    
    def __init__(self, pos):
        Entity.__init__(self, pos, ENTITY_SIZE, LAYER_BLOCKS)
        self.tex = 'carried/wood_pile.png'
        self.carried_by = None
        self.height = ENTITY_SIZE.x

    def update(self):
        Carryable.update(self)

class Flag(Mover):
    def __init__(self, pos, team):
        Entity.__init__(self, pos, ENTITY_SIZE,LAYER_BLOCKS)
        self.tex = team+'_flag.png'
        self.height= ENTITY_SIZE.x


class FruitPatch:

    def __init__(self, pos_x, pos_y, width, height,edge=2):
        halfwidth = width*0.5
        halfheight = height*0.5
        d_max = sqrt(halfwidth*halfwidth+\
                     halfheight*halfheight)
        for x in range(width):
            for y in range(height):
                if random.random() < 0.025:
                    try:
                        Carryable(vector2(pos_x+x, pos_y+y))
                    except CellFull:
                        pass


class Building:
    def __init__(self, pos_x, pos_y, width, height):
        print "building a building"
        #add the baseline
        self.parts = {}
        for x in range(width):
            self.add_part(pos_x+x, pos_y + height, 0, 'wall.png')
                        
        #add in the corner walls        
        self.add_part(pos_x, pos_y+height, 0, 'building_corner_left.png')
        self.add_part(pos_x+width-1, pos_y+height, 0, 'building_corner_right.png')
    

        #put a door in that shit
        self.add_part(pos_x+width/2, pos_y+height,0, 'door.png')
        
        #add the roof tops
        self.add_part(pos_x, pos_y, 1, 'roof_top_left_0.png')
        self.add_part(pos_x+1, pos_y, 1, 'roof_top_left_1.png')
        self.add_part(pos_x+width-2, pos_y, 1, 'roof_top_right_1.png')
        self.add_part(pos_x+width-1, pos_y, 1, 'roof_top_right_0.png')

        #add the roof bottoms
        y_2 = pos_y+height-1
        self.add_part(pos_x, y_2, 1, 'roof_bottom_left_0.png')
        self.add_part(pos_x+1, y_2, 1, 'roof_bottom_left_1.png')
        self.add_part(pos_x+width-2, y_2, 1, 'roof_bottom_right_1.png')
        self.add_part(pos_x+width-1, y_2, 1, 'roof_bottom_right_0.png')
        #add the roof tiles
        for y in range(height-2):
            for x in range(width):
                if x >= width/2:
                    tex = 'roof_right.png'
                else:
                    tex = 'roof_left.png' 
                self.add_part(pos_x+x, pos_y+y+1, 1, tex)
        
    def add_part(self, x, y, height, tex):
        if (x,y,height) in self.parts:
            part = self.parts[(x,y,height)]
            part.tex = tex
            part.layer = LAYER_BLOCKS+height
        else:
            part = SolidBlock(vector2(x,y), tex=tex, layer=LAYER_BLOCKS+height)
            self.parts[(x,y,height)] = part
        
class SolidBlock(Mover):
    def __init__(self, pos, tex = 'grey_box.png', layer=LAYER_BLOCKS):
        Entity.__init__(self, pos, ENTITY_SIZE, layer)
        self.tex = tex
        self.solid = True


