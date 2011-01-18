from random import *
from vector2 import *
from engine import *



BOMB_COOLDOWN = 10
LASER_COOLDOWN = 5

LAYER_BLOCKS = 0



class Mover(Entity):

    def try_move(self, push_dir):
        if push_dir != ZERO_VECTOR:
            target = self.pos + push_dir;
            other_target = target+push_dir;

            ents = engine.grid.get_entities(target.x,
                                            target.y)


            other_ents = engine.grid.get_entities(other_target.x,
                                            other_target.y)

            blocked = False
                    
            if  LAYER_BLOCKS in ents:
              if  LAYER_BLOCKS in other_ents:
                blocked = True
              else:
                for layer in ents:
                  ent = ents[layer]
                  if not self.can_push(ent):
                    blocked = True
                if not blocked:
                    for layer in ents:
                        self.push(ents[layer])
                        ents[layer].take_push(self, other_target)
                
            if not blocked:  
              self.move(target)

            return not blocked
        return True


class Dude(Mover):
    """a single object that moves around in the game"""

    def __init__(self,owner):
        Entity.__init__(self, vector2(1,1), ENTITY_SIZE )

        self.owner = owner
        self.solid = True
        self.dir = ZERO_VECTOR
        self.last_dir = ZERO_VECTOR
        self.act = None
        self.bomb_cooldown = BOMB_COOLDOWN
        self.laser_cooldown = LASER_COOLDOWN
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



    def die(self, killer):
        if self.on_die:
            self.on_die()
        killer.on_kill(self)
        Entity.die(self)
                
      
class TeamBlock(Entity):
    def __init__(self, team, pos=ZERO_VECTOR):
        
        Entity.__init__(self, pos, ENTITY_SIZE)
        self.team = team
        self.tex = self.team+'_tile.png'
        self.solid = True

    def update(self):
        pass 

    def take_push(self, pusher, target):
        self.move(target)


class RedBlock(TeamBlock):

    def __init__(self,pos):
        TeamBlock.__init__(self,'red',pos)
        
    

class BlueBlock(TeamBlock):

    def __init__(self,pos):
        TeamBlock.__init__(self,'blue',pos)

class SolidBlock(Entity):
    def __init__(self, pos):
        
        Entity.__init__(self, pos, ENTITY_SIZE)
        
        self.tex = 'box.png'
        self.solid = True


    def update(self):
        pass
    def get_state(self):
        return Entity.get_state(self)



class Booster(Entity):

    def __init__(self, pos, direction):
        Entity.__init__(self, pos, ENTITY_SIZE)
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
            self.die()
        else:
            self.move(target)



class Snockerball(Mover):
    def __init__(self,pos=ZERO_VECTOR):
        self.layer = LAYER_BLOCKS
        Entity.__init__(self, pos, ENTITY_SIZE)
        self.tex = 'snockerball.png'
        self.team = None
        self.dir = ZERO_VECTOR
    
    def can_push(self, pushee):
        can = isinstance(pushee, Booster)
    
        return can
  
    def push(self, pushee):
        if isinstance(pushee, Booster):
            print "boosted!",pushee.dir
            self.dir += pushee.dir

    def take_push(self, pusher, target):
        self.dir += target - self.pos
        self.move(target)
        
        
    def update(self):

        v_x = self.dir.x+1-1
        v_y = self.dir.y+1-1

        while v_x > 0:
            if not self.try_move(LEFT):
                self.dir.x = - self.dir.x
                break 
            v_x -= 1
                

        while v_x < 0:
            if not self.try_move(RIGHT):
                self.dir.x = -self.dir.x
                break
            v_x += 1
               

        while v_y > 0:
            if not self.try_move(UP):
                self.dir.y = -self.dir.y
                break 
            v_y -= 1
                

        while v_y < 0:
            if not self.try_move(DOWN):
                self.dir.y = - self.dir.y
                break
            v_y += 1
                


    def die(self,killer):
        Entity.die(self, killer)
        Diamond()


