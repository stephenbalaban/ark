from random import *
from vector2 import *
from engine import *




LAYER_GOALS = 0
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
                    
            if  len(ents):
                #see if this guy to the right can move
                    
                for layer in ents:
                    other = ents[layer] 
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
    """a single object that moves around in the game"""

    def __init__(self,owner):

        self.act = None
        Entity.__init__(self, vector2(1,1), ENTITY_SIZE, LAYER_BLOCKS )

        self.owner = owner
        self.solid = True
        self.dir = ZERO_VECTOR
        self.last_dir = ZERO_VECTOR
        self.act = None
        self.on_die = None
        self.frames = 2
        self.team = random.choice(['blue','red'])
        self.tex = self.team+'_right'        

    def push(self, pushee):
        pass
 
     
    def can_push(self, obj):
        can = isinstance(obj, Snockerball)
        can = can or isinstance(obj, Booster)
        can = can or (isinstance(obj, TeamBlock) and obj.team == self.team)
        return can 
    def can_smash(self, obj):
        can = isinstance(obj, Goal)
        return can
        
    def update(self):
        self.try_move(self.dir)
        if self.dir == UP:
            self.change_tex(self.team+'_up')
        elif self.dir == DOWN:
            self.change_tex(self.team+'_down')
        elif self.dir == RIGHT:
            self.change_tex(self.team+'_right')
        elif self.dir == LEFT:
            self.change_tex(self.team+'_left')
        if self.dir.x !=0 or self.dir.y != 0:
            self.last_dir = self.dir
        if self.act == 'place':
            place = self.pos+self.last_dir
            print self.dir

            if not LAYER_POWERUPS in engine.grid.get_entities(place.x, place.y):
                Booster(place, self.last_dir)
            self.act = None

    def die(self, killer):
        if self.on_die:
            self.on_die()
        killer.on_kill(self)
        Entity.die(self)
                


class  Goal(Mover):
    
    def __init__(self, team,pos=ZERO_VECTOR):
        Entity.__init__(self,pos, ENTITY_SIZE, LAYER_GOALS)
        self.team = team
        self.tex = team + "_tile_1.png" 
    def update(self): 
        pass

    def take_smash (self, smasher):
        if isinstance(smasher, Snockerball):
            smasher.die()
            print "GOOOOOOOOOOOOOOOOOAL", self.team

            Snockerball(vector2(GRID_SIZE/2, GRID_SIZE/2))
     
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



class RedBlock(TeamBlock):

    def __init__(self,pos):
        TeamBlock.__init__(self,'red',pos)
        
    

class BlueBlock(TeamBlock):

    def __init__(self,pos):
        TeamBlock.__init__(self,'blue',pos)


class SolidBlock(Mover):
    def __init__(self, pos):
        
        Entity.__init__(self, pos, ENTITY_SIZE)
        
        self.tex = 'box.png'
        self.solid = True


    def update(self):
        pass
    def get_state(self):
        return Entity.get_state(self)



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
        



class Snockerball(Mover):
    def __init__(self,pos=ZERO_VECTOR):
        Entity.__init__(self, pos, ENTITY_SIZE, LAYER_BLOCKS)
        self.tex = 'snockerball.png'
        self.team = None
        self.dir = ZERO_VECTOR
    
    def can_push(self, pushee):
        can = isinstance(pushee, Snockerball)
        return can 
    def can_smash(self, victim):
        can = isinstance(victim, Booster)
        can = can or isinstance(victim, Goal)
        return can

    def push(self, pushee):
        if isinstance(pushee, Booster):
            self.dir += pushee.dir

    def smash(self, other):
        if isinstance(other, Booster):
            self.dir += other.dir

    def take_push(self, pusher, target):
        self.dir += self.pos - pusher.pos
        self.move(target)

        
    def update(self):


        dx = clamp(-2,self.dir.x,2 )
        dy = clamp(-2,self.dir.y, 2)
        self.dir.x = dx
        self.dir.y = dy
        while dx  or dy:

            if dx > 0:
                if not self.try_move(RIGHT):
                    self.dir.x = - self.dir.x
                    dx = 0
                else:
                    dx -= 1
            
            if dx < 0:
                if not self.try_move(LEFT):
                    self.dir.x = - self.dir.x
                    dx = 0
                else:
                    dx += 1


            if dy < 0:
                if not self.try_move(UP):
                    self.dir.y = - self.dir.y
                    dy =0
                else:
                    dy += 1

            if dy > 0:
                if not self.try_move(DOWN):
                    self.dir.y = - self.dir.y
                    dy =0 
                else:
                    dy  -= 1


