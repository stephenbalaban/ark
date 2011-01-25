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

class Dude(Mover):

    def __init__(self,owner):

        pos = engine.grid.get_free_position(LAYER_BLOCKS)

        Entity.__init__(self, pos, vector2(8,16), LAYER_BLOCKS )

	self.net_vars['anim'] = True
	self.net_vars['walking'] = True

        self.act = None
        self.owner = owner
        self.solid = True
        self.dir = ZERO_VECTOR
        self.last_dir = ZERO_VECTOR
        self.act = None
        self.on_die = None
        self.frames = 2
        self.team = random.choice(['blue','red'])
        self.tex = 'warrior_right'        
	self.anim = 'dude'
	self.walking = False

    def push(self, pushee):
        pass
 
     

    def update(self):
        self.try_move(self.dir)
        if self.dir == UP:
            self.change_tex('warrior_up')
        elif self.dir == DOWN:
            self.change_tex('warrior_down')
        elif self.dir == RIGHT:
            self.change_tex('warrior_right')
        elif self.dir == LEFT:
            self.change_tex('warrior_left')
        if not self.dir.is_zero():
            self.last_dir = self.dir
	    self.walking = True
	else:
	    self.walking = False


    def die(self, killer):
        if self.on_die:
            self.on_die()
        killer.on_kill(self)
        Entity.die(self)
                


class  Candy(Mover):
    def __init__(self, color, pos=ZERO_VECTOR):
        Entity.__init__(self,pos, ENTITY_SIZE, LAYER_BLOCKS)
        self.color = color
        self.tex = color  + "_candy.png" 

   
    def update(self): 
        pass

     
class TeamBlock(Mover):
    def __init__(self, team, pos=ZERO_VECTOR):
        Entity.__init__(self, pos, ENTITY_SIZE, LAYER_GOALS)
        self.team = team
        self.tex = self.team+'_tile.png'
        self.solid = True

    def update(self):

        pass 

    def can_push(self, victim):
        can = isinstance(victim, TeamBlock)
        return can



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

class Tree(Mover):
    def __init__(self, pos):
	Entity.__init__(self, pos, vector2(8,16), LAYER_BLOCKS)
	self.tex = 'full_tree.png'

    
class Forest:

    def __init__(self, pos_x, pos_y, width, height,edge=2):
        halfwidth = width*0.5
        halfheight = height*0.5
        d_max = sqrt(halfwidth*halfwidth+\
                     halfheight*halfheight)
        for x in range(width):
            for y in range(height):

                if x < edge or x > width - edge:
                    dx = x - halfwidth
                else:
                    dx = 0
                if y < edge or y > height - edge:
                    dy = y - halfheight
                else:
                    dy = 0
                 
                d = sqrt(dx*dx+dy*dy)
                p = 1.0 - d/d_max
                 
                if random.random() <= p:
                    Tree(vector2(pos_x+x, pos_y+y))


class Building:
    def __init__(self, pos_x, pos_y, width, height):
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


class BlinkyBlock(Mover):

    def __init__(self, pos,powered=None):
        
        Entity.__init__(self, pos, ENTITY_SIZE, LAYER_BLOCKS)
        if powered == None:
	    self.powered = random.choice([True, False])
	else:
	    self.powered = powered
	self.blink_period = 10
	self.cool_period = 4
	self.color = random.choice(['blue', 'purple'])
        self.tex = self.color+'_candy.png'
        self.solid = True
	self.blink_ticks_left = random.choice(range(self.blink_period))
	self.cool_ticks_left = 0
	self.last_blink_frame = -2

    def update(self):

	if self.powered:
	    if self.blink_ticks_left == self.blink_period:
		self.change_tex(self.color+'_candy.png')
	    self.blink_ticks_left -= 1
	    if self.blink_ticks_left <= 0:
		self.blink()
	else:
	    if self.cool_ticks_left == self.cool_period:
		self.change_tex(self.color+'_candy.png')

	    self.cool_ticks_left -= 1
       
	    if self.cool_ticks_left <= 0: 
		neighbors = engine.grid.get_neighbors(self.pos)
		for direction in neighbors:
		    if LAYER_BLOCKS in neighbors[direction]:
			guys = neighbors[direction]
			guy = guys[LAYER_BLOCKS]
			if isinstance(guy, BlinkyBlock) and guy.was_blinking():
			    self.blink()
	
    def was_blinking(self):
	return self.last_blink_frame == engine.current_frame - 1
    def	blink(self):
	self.change_tex(self.color+'_candy_on.png')
	if self.powered:
	    self.blink_ticks_left = self.blink_period
	else:
	    self.cool_ticks_left = self.cool_period
	self.last_blink_frame = engine.current_frame


class Booster(Mover):

    def __init__(self, pos, direction=None):
        Entity.__init__(self, pos, ENTITY_SIZE, LAYER_POWERUPS)
        if not direction:
            direction = random.choice([UP,DOWN,LEFT,RIGHT])
        self.angle = direction.angle()
        self.dir = direction
        self.tex = 'boost_arrow.png'
        self.solid = True

    def can_push(self, pushee):
        return False

    def update(self):
        pass
    def get_state(self):
        return Entity.get_state(self)

    def take_push(self, pusher, target):
        if isinstance(pusher,Snockerball): 
            pass
        else:
            self.move(target)
        
