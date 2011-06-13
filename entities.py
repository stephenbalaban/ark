from random import *
from vector2 import *
from engine import *


from scribit import log, timed, logged

LAYER_GROUND = 0
LAYER_WATER = LAYER_GROUND+1
LAYER_GROUND_DETAIL = LAYER_WATER+1
LAYER_BLOCKS = LAYER_GROUND_DETAIL +1 
LAYER_CARRIED = LAYER_BLOCKS + 1

CARRIED_HEIGHT= ENTITY_SIZE.x*3.5
class Air: 
    def __init__(self,pos):
        self.pos = pos

    def can_smash(self, other):
        return True

    def smash(self, other):        
        if isinstance(other, Terrain):
            if other.terrain_type == 'grass':
                PlowedPatch(pos=other.pos)

        elif isinstance(other, Tree):
            other.die()
            WoodPile(pos=other.pos)

class Flammable:
    pass


ACT_PLACE = 1
class Mover(Entity):

    def try_move(self, push_dir):

        if not (push_dir.x == 0  and push_dir.y == 0):
            target = self.pos + push_dir;
            other_target = target+push_dir;

            ents = engine.metagrid.get_entities(target.x,
                                                target.y)

            if LAYER_GROUND in ents:
                if not self.can_travel(ents[LAYER_GROUND].terrain_type):
                    return False
                    
            other_ents = engine.metagrid.get_entities(other_target.x,
                                                   other_target.y)
            blocked = False
            if  self.layer in ents:
                #see if this guy to the right can move
                other = ents[self.layer] 
                if isinstance(other, Mover):
                    if self.can_push(other) and other.try_move(push_dir):
                        other.take_push(self, other_target)
                        self.push(other)
                    else:
                        blocked = True
                        
            if not blocked:  
                self.move(target)
            return not blocked

        return True

    def can_travel(self, terrain_type):
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
        self.move(victim.pos)
        


            
    def take_push(self, pusher, target):
        self.move(target)

    def take_smash(self,  smasher):
        self.die(smasher)

class Carryable:

    def smash(self, victim):
        self.carried_by = None
        self.height = ENTITY_SIZE.x*0.5
        engine.metagrid.remove_entity(self, moving=True)
        self.layer = LAYER_BLOCKS
        self.pos = victim.pos
        engine.metagrid.add_entity(self, moving=True)


class Plantable:
    pass

class Craftable:
    pass

class Fruit(Carryable, Plantable, Flammable, Mover):

    def __init__(self, **kwargs):
        kwargs['layer'] = LAYER_BLOCKS
        Entity.__init__(self, **kwargs)
        self.type = random.choice(['lemon',
                                  'cherry'])
        self.tex = "carried\\%s.png" % self.type
        self.height = ENTITY_SIZE.x*0.5
        self.carried_by = None

    def can_smash(self, victim):
        can = isinstance(victim, PlowedPatch)
        can = can or isinstance(victim, Terrain)
        return can

    def smash(self, victim):
        #check to see if we can plant this object                
        if isinstance(victim, PlowedPatch):
            if victim.state == 'unplanted':
                victim.plant(self)
                self.tex = 'none.png'
                return
        self.carried_by = None 
        Carryable.smash(self,victim)
        

class Walker:
    """objects that choose a direction and move in that direction
    make sure you set last_sir"""

    def update(self):
        if not self.dir.is_zero():

            if (not hasattr(self, 'last_dir'))\
                        or self.dir == self.last_dir:
                if self.try_move(self.dir):
                    if self.carrying:
                        self.carrying.move(self.pos)
            self.last_dir = self.dir
        
@RegisterPersisted
class Dude(Mover, Walker, Updater):

    def __init__(self,**params):

        pos = params.get('pos') or engine.metagrid.get_free_position(LAYER_BLOCKS)
        params['pos'] = pos
        params['layer'] = params.get('layer') or LAYER_BLOCKS
        Entity.__init__(self, **params)

        self.height = ENTITY_SIZE.x*0.5;
        self.act = None
        self.solid = True
        self.dir = ZERO_VECTOR
        self.last_dir = RIGHT
        self.act = None
        self.on_die = None
        self.frames = 2
        self.team = random.choice(['blue','red'])
        self.dude_class = 'warrior'
        self.anim = 'dude'
        #states are: standing, moving, using
        self.state = 'standing'
        self.carrying = None
        self.net_vars['anim'] = True

    def push(self, pushee):
        Mover.push(self, pushee)
 
    def can_travel(self, terrain_type):
        return True 

    def can_push(self,other):
        can =  isinstance(other, WoodPile) or\
                isinstance(other, FirePuff) or\
                isinstance(other, Sheep) or\
                isinstance(other, Fruit)

        return can


    def update(self):

        if not self.dir.is_zero():
            Walker.update(self)
        elif self.act == 'use':
            self.state = 'using'
            self.use()
        else:
            self.state = 'standing'
        self.update_texture()

        
             
    def use(self):
        target_pos = self.pos + self.last_dir
        dudes = engine.get_entities(target_pos.x,target_pos.y)
        move = False
        
        if self.carrying:  
            smasher = self.carrying
            for layer in [LAYER_BLOCKS, 
                          LAYER_GROUND_DETAIL,
                          LAYER_GROUND]:
                if layer in dudes: 
                    if smasher.can_smash(dudes[layer]):
                        log('%s can smash %s' % (smasher, dudes[layer]))
                        self.carrying = None
                        smasher.smash(dudes[layer])
                    break
            return
        #not carrying anything  
        #check for an item to act on
        neighbors = engine.metagrid.get_neighbors(self.pos)


        #see if you're looking at a water square
        if self.last_dir in neighbors:
            dudes = neighbors[self.last_dir]
            if not LAYER_BLOCKS in dudes and\
                dudes[LAYER_GROUND].terrain_type == 'water':

                WaterDrop(pos=self.pos+self.last_dir)
                return 

        if self.last_dir in neighbors:
            dudes = neighbors[self.last_dir]
            for layer in [LAYER_BLOCKS,
                            LAYER_GROUND_DETAIL,
                            LAYER_GROUND]:
                if layer in dudes:
                    other_guy = dudes[layer]
                    if isinstance(other_guy, Carryable):
                        self.carry_item(other_guy)
                    else: 
                        Air(self.pos).smash(other_guy)
                    #once we've encounterd an object, we're done
                    break

    def carry_item(self, item):
        item.carried_by = self
        item.height = CARRIED_HEIGHT 
        engine.remove_entity(item, moving=True)
        item.layer = LAYER_CARRIED
        item.pos = self.pos
        engine.add_entity(item, moving=True) 
        self.carrying = item 

    def update_texture(self):
        self.tex = ('%s/%s/%s' % (self.dude_class,
                                  self.state,
                                  DIR_NAMES[self.last_dir]))
            
       



    def die(self, killer):
        if self.on_die:
            self.on_die()
        if killer and hasattr(killer, 'on_kill'):
            killer.on_kill(self)
        Entity.die(self)

@RegisterPersisted
class Player(Dude): pass

@RegisterPersisted
class Roamer(Walker):

    def __init__(self, **params):
        self.reset_move_ticks()


    def reset_move_ticks(self):
        self.move_ticks =  5 + random.randint(0, 5)

    def update(self):
        #set dir 
        if self.move_ticks == 0:
            if random.random() < 0.1:
                self.dir = random.choice([UP,DOWN,LEFT,RIGHT])
            self.reset_move_ticks()
            Walker.update(self)

        self.move_ticks -= 1
            #see if there are any plants in the area, if there are, go afer them
        self.update_texture()
    
   
@RegisterPersisted
class Chaser(Walker):

    def __init__(self,**params):
        self.target = None
    

    def update(self):
        if not self.target:
            self.find_target()
        else:
            #figure out what direction to go to the target
            #go that direction
            target_dir = self.target.pos - self.pos

            if target_dir.x > 0:
                target_pos = self.pos + LEFT
            elif target_dir.x < 0:
                target_pos = self.pos + RIGHT
            elif target_dir.y < 0:
                target_pos = DOWN
            elif target_dir.y > 0:
                target_pos = UP
            else:
                target_pos = self.pos

            self.move(target_pos)

    
    def find_target(self):
        return None

class Seeker:

    def get_dir_for_target(self, other):
        away = other.pos - self.pos
        choices = [ZERO_VECTOR]
        
        correct_bonus = 10 
        if away.x > 0:
            for x in range (correct_bonus):
                choices.append(RIGHT)
            choices.append(UP)
            choices.append(DOWN)
        if away.x < 0:
            for x in range(correct_bonus):
                choices.append(LEFT)
            choices.append(UP)
            choices.append(DOWN)

        if away.y > 0:
            for x in range(correct_bonus):
                choices.append(DOWN)
            choices.append(LEFT)
            choices.append(RIGHT)

        if away.y < 0:
            for x in range(correct_bonus):
               choices.append(UP)
            choices.append(LEFT)
            choices.append(RIGHT)

        return random.choice(choices)



@RegisterPersisted
class Sheep(Seeker, Dude, Roamer, Carryable, Flammable):

    def __init__(self, **params):
        params['scale'] = params.get('scale') or 0.5+ random.random()*0.5 
        Dude.__init__(self,**params)
        self.dude_class = 'sheep'
        self.update_texture() 
        self.carried_by = None
        self.carrying = None
        self.state = 'walking'
        self.reset_move_ticks()



    def can_smash(self, other):
        can = isinstance(other, Terrain)
        can = can or isinstance(other, FirePuff)
        return can


    def can_travel(self, ttype):
        return not ttype in [ 'water' ]

    def smash(self, other):
        if isinstance(other, FirePuff):
            other.die(self)
            self.die(self)
            FireRing(pos=other.pos)
        else:
            Carryable.smash(self, other) 


    def can_push(self, other):
        return False

    def update(self):

        if self.carried_by:
            return 

        if self.scale < 1:
            self.scale += random.random()*0.001
        else:
            if random.random() < 0.001:
                #find a free position near this guy and spawn a sheep
                neighbors = engine.metagrid.get_neighbors(self.pos)

                for dir in neighbors:
                    if not LAYER_BLOCKS in neighbors[dir]:
                        Sheep(pos=self.pos+dir,
                              scale=0.5)
                        break

        def acceptor(ent):
            return isinstance(ent, Wolf) or\
                    isinstance(ent, Player) or\
                    isinstance(ent, Shrub)

        nearest = engine.metagrid.find_nearest(self.pos.x, 
                                  self.pos.y,
                                   LAYER_BLOCKS,
                                   GRID_SIZE/2,
                                   acceptor)
        if not nearest:
            Roamer.update(self)
        else:
            towards = self.get_dir_for_target(nearest)
            if not towards == ZERO_VECTOR:
                if isinstance(nearest, Shrub):
                    if towards.length() == 1:
                        nearest.die()
                        return
                    else:
                        self.last_dir = towards
                        self.dir = towards
                else:
                    away = DIR_OPPOSITES[towards]
                    self.last_dir = away 
                    self.dir = away
                Walker.update(self)

    def use(self):
        #sheep eat plants
        if self.target:
            self.target.die()
            self.target.parent.harvest()
            self.target = None
 

        wolf = engine.metagrid.find_nearest(self.pos.x, 
                                  self.pos.y,
                                   LAYER_BLOCKS,
                                   4,
                                   acceptor)
        if not wolf:
            Roamer.update(self)
        else:
            towards = self.get_dir_for_target(wolf)
            if not towards == ZERO_VECTOR:
                away = DIR_OPPOSITES[towards]
                self.last_dir = away 
                self.dir = away
                Walker.update(self)

    def use(self):
        #sheep eat plants
        if self.target:
            self.target.die()
            self.target.parent.harvest()
            self.target = None
            self.ai_state = 'roaming'
            self.act =  None
 
@RegisterPersisted
class Wolf(Seeker, Roamer, Chaser, Dude):

    def __init__(self, **params):
        Dude.__init__(self,**params)
        Roamer.__init__(self)
        Chaser.__init__(self)
        self.dude_class = 'wolf'
        self.state = 'walking'
        self.update_texture() 
        self.carried_by = None
        self.carrying = None


    def can_smash(self, other):
        can = isinstance(other, Terrain)
        return can

    def can_travel(self, ttype):
        return not ttype in [ 'water' ]


    def update(self):

        def acceptor(ent):
            return isinstance(ent, Sheep)

        sheep = engine.metagrid.find_nearest(self.pos.x, 
                                  self.pos.y,
                                   LAYER_BLOCKS,
                                   GRID_SIZE,
                                   acceptor)
        if not sheep:
            Roamer.update(self)
        else:
            towards = self.get_dir_for_target(sheep)
            if not towards == ZERO_VECTOR:
                self.last_dir = towards 
                self.dir = towards 
                Walker.update(self)


    def smash(self, other):
        if isinstance(other, Terrain):
            Carryable.smash(self,other)

    def can_push(self, other):
        return False

    def use(self):
        pass


   
@RegisterPersisted
class Terrain(Entity):
    
    def __init__(self, **kwargs):
        kwargs['tex'] = kwargs.get('tex') or 'grass.png'
        kwargs['terrain_type'] = kwargs.get('terrain_type') or 'grass'
        kwargs['neighbor_types'] = kwargs.get('neighbor_types') or  {}
        Entity.__init__(self,**kwargs)
        
        if self.neighbor_types == {}:
            for dir in ORDINALS:
                self.neighbor_types[dir] = 'grass'
        self.update_tex()
       
    
    def to_water(self):
        self.terrain_type = 'water'

        def update_visitor(neighbor, dir):
            if isinstance(neighbor, Terrain):
                #log ('%s updating terrain' % neighbor)
                neighbor.update_neighbor_types()
                neighbor.update_tex()

        def water_visitor(neighbor, dir):
            #log ('%s is now water'  % neighbor)
            neighbor.terrain_type = 'water'
            neighbor.update_tex()

        self.percolate(GRID_SIZE, 0.8, water_visitor)
        #log('percolating update')
        self.percolate(GRID_SIZE, 1.0, update_visitor, {})
        self.update_tex()

    def start_forest(self, spawn_type, distance):
        def tree_visitor(neighbor, dir):
            if neighbor.terrain_type == 'water': 
                return
            dist = (neighbor.pos - self.pos).length()
            if dist == 0:
                dist = 1

            prob = distance/(dist*dist)
            if random.random() < prob:
                if not LAYER_BLOCKS in\
                    engine.get_entities(neighbor.pos.x, neighbor.pos.y):
                    spawn_type(layer=LAYER_BLOCKS,pos=neighbor.pos)
        self.percolate(distance, 0.8, tree_visitor)
        tree_visitor(self, None)



    def percolate(self, ticks, density, visitor, visited = {}, root = None): 
        neighbors = engine.metagrid.get_neighbors(self.pos)
        if root == None:
            root = self
        if (root.pos - self.pos).length() > ticks: 
            return 
        for  dir in ALL_DIRS:
            if dir in neighbors: 
                if LAYER_GROUND in neighbors[dir]:
                    neighbor = neighbors[dir][LAYER_GROUND]
                    if not neighbor in visited:
                        visited[neighbor] = True
                        visitor(neighbor, dir)
                        if ticks > 0 and random.random() <  density:
                            neighbor.percolate(ticks, density, 
                                            visitor, visited, root)


                
    def update_neighbor_types(self):        
        neighbors = engine.metagrid.get_neighbors(self.pos)
        for op_dir in neighbors:
            these = neighbors[op_dir]
            if LAYER_GROUND in these:
                neighbor = these[LAYER_GROUND]
                self.neighbor_types[op_dir] = neighbor.terrain_type
    


    def update_tex(self):
        self.tex = '%s/%s/%s/%s/%s.png' % (self.terrain_type,
                                         self.neighbor_types[UP],
                                         self.neighbor_types[RIGHT],
                                         self.neighbor_types[DOWN],
                                         self.neighbor_types[LEFT])

@RegisterPersisted
class Road(Entity):

    def __init__(self, pos, is_vertical):
        Entity.__init__(self, pos, ENTITY_SIZE, LAYER_GROUND)
        if is_vertical:
                        self.tex = 'road_vertical.png'
        else:
                        self.tex = 'road_horizontal.png'


@RegisterPersisted
class Shrub(Carryable, Mover):

    def __init__(self, pos,parent):
        Entity.__init__(self, pos=pos,size=ENTITY_SIZE,layer=LAYER_BLOCKS)
        self.plant_size = 0
        self.tex = '/plants/shrub/0.png'
        self.parent = parent        

    def grow(self):
        self.plant_size += 1
        self.tex = '/plants/shrub/1.png'



@RegisterPersisted
class PlowedPatch(Mover, Updater):

    PLANT_GROWTH_TICKS = 20
    def __init__(self, **kwargs):
        kwargs['size'] = kwargs.get('size') or ENTITY_SIZE
        kwargs['layer'] =  kwargs.get('layer') or LAYER_GROUND_DETAIL
        Entity.__init__(self,**kwargs)
        #check for neighbors above and below, changing them if necessary
        neighbors = engine.metagrid.get_neighbors(self.pos)
        has_neighbors = {UP:False, DOWN: False}
        for dir in [UP, DOWN]:
            if dir in neighbors:
                ents = neighbors[dir]
                if LAYER_GROUND_DETAIL in ents:
                    ent = ents[LAYER_GROUND_DETAIL]
                    if isinstance(ent, PlowedPatch):
                        ent.new_neighbor(dir)
                        has_neighbors[dir] = True
        if has_neighbors[UP] and has_neighbors[DOWN]:
            self.type = 'middle'
        elif has_neighbors[UP]:
            self.type = 'bottom'
        elif has_neighbors[DOWN]:
            self.type = 'top'
        else:
            self.type = 'solo'
            
        self.tex = "plowed/unplanted/%s.png" % self.type
        self.state = 'unplanted'
        self.planted = None
        self.plant_growth_ticks = 0
        self.growing = None

    def plant(self, seed):
        self.planted = seed
        seed.tex = 'none.png'
        self.state = 'planted'
        self.update_tex()
        self.plant_growth_ticks = PlowedPatch.PLANT_GROWTH_TICKS
 

    def new_neighbor(self, dir):
        if self.type == 'solo':
            if dir == UP:
                self.type = 'top'
            elif dir == DOWN:
                self.type = 'bottom'

        elif self.type == 'top':
            if dir == DOWN:
                self.type = 'middle'
        elif self.type == 'bottom':
            if dir == UP:
                self.type = 'middle'
        self.update_tex()

    def update_tex(self):        
        self.tex = 'plowed/%s/%s.png' % (self.state, self.type)

    def harvest(self):
        self.planted = None
        self.plant_growth_ticks = None
        self.growing = None

    def update(self):        
        if self.plant_growth_ticks:
            self.plant_growth_ticks -= 1
            if self.plant_growth_ticks == 0:
                if self.growing == None:
                    try:
                        self.growing = Shrub(self.pos,self)
                        self.plant_growth_ticks = PlowedPatch.PLANT_GROWTH_TICKS
                    except CellFull:
                        self.plant_growth_ticks = 0
                    
                else:
                    self.growing.grow()


@RegisterPersisted
class Tree(Mover):
    def __init__(self, **kwargs):
        kwargs['tex'] = 'full_tree.png'
        kwargs['layer'] = LAYER_BLOCKS
        kwargs['height'] = ENTITY_SIZE.y*2
        Entity.__init__(self, **kwargs)

    def die(self):
        Entity.die(self)


@RegisterPersisted
class FireRing(Entity, Updater):

    def __init__(self, **kwargs):
        kwargs['total_distance'] = kwargs.get('total_distance') or   5
        kwargs['current_distance'] = kwargs.get('current_distance') or  5 
        kwargs['layer'] = kwargs.get('layer') or  LAYER_BLOCKS
        Entity.__init__(self,**kwargs)

    def update(self):
        self.current_distance -= 1
        if self.current_distance == 4:

            #log ('Fire ring updating radius %d' % self.current_distance)
            def circle_visitor(x,y):
                ents = engine.metagrid.get_entities(x,y)
                if  LAYER_BLOCKS in ents:
                    dude = ents[LAYER_BLOCKS]
                    if not isinstance(ents, Flammable):
                        return
                    else:
                        ents[LAYER_BLOCKS].die()
                log('Fire ring at %d,%d'% (x,y))
                log('Distance: %0.3f' % ( ((x-self.pos.x)**2 + (y -self.pos.y)**2)**0.5))
                FirePuff(pos=vector2(x,y))
            engine.metagrid.visit_circle(self.pos.x, self.pos.y, self.current_distance, circle_visitor)
        else:
            #log('FireRing died')
            self.die()

        
            
@RegisterPersisted
class FirePuff(Entity, Mover, Carryable):

    def __init__(self, **kwargs):
        kwargs['tex'] = 'fire.png'
        kwargs['layer'] = LAYER_BLOCKS
        kwargs['height'] = ENTITY_SIZE.y
        Entity.__init__(self,**kwargs)

    def can_smash(self, other):
        return isinstance(other, Flammable) or\
               isinstance(other, Terrain)


    def smash(self, other):
        if isinstance(other, Flammable):
            other.die(self)
            self.die(self)
            FireRing(pos=other.pos)
        else:
            Carryable.smash(self,other)

@RegisterPersisted
class WaterDrop(Entity, Mover,Carryable):
    def __init__(self, **kwargs):
        kwargs['tex'] = 'carried/water.png'
        kwargs['layer'] = LAYER_BLOCKS
        kwargs['height'] = ENTITY_SIZE.y
        Entity.__init__(self,**kwargs)
        self.tex  = 'carried/water.png'

    def can_smash(self, other):
        return isinstance(other, FirePuff) or\
               isinstance(other, Terrain)

 

    def smash(self, other):
        if isinstance(other, FirePuff):
            other.die(self)
            self.die(self)
        else:
            Carryable.smash(self,other)



@RegisterPersisted
class WoodPile(Mover, Carryable, Flammable):
    
    def __init__(self, **kwargs):
        kwargs['tex'] = kwargs.get('tex') or 'carried/wood_pile.png'
        kwargs['height'] = kwargs.get('height') or ENTITY_SIZE.x
        kwargs['layer'] = kwargs.get('layer') or LAYER_BLOCKS
        Entity.__init__(self,**kwargs)
        self.carried_by = None


    def can_smash(self, other):
        can = isinstance(other, Terrain)
        can = can or isinstance(other, PlowedPatch)
        return can

    def smash(self, other):
        if isinstance(other, Terrain):
            Carryable.smash(self,other)
           
        elif isinstance(other, PlowedPatch):
            other.die()            
            self.die()
            Fence(pos=other.pos) 

@RegisterPersisted
class Fence(Mover, Entity, Flammable):

    def __init__(self, **kwargs):
        kwargs['layer'] = kwargs.get('layer') or LAYER_BLOCKS
        Entity.__init__(self,**kwargs)
        self.neighbor_fences = {}

        neighbors = engine.metagrid.get_neighbors(self.pos)

        for dir in ORDINALS:
            self.neighbor_fences[dir] = 'no'
            if dir in neighbors:
                if LAYER_BLOCKS in neighbors[dir]:
                    this_guy = neighbors[dir][LAYER_BLOCKS]
                    if isinstance(this_guy, Fence):
                        this_guy.neighbor_fences[DIR_OPPOSITES[dir]] = 'yes'
                        this_guy.update_texture()
                        self.neighbor_fences[dir] = 'yes'

        self.update_texture()

    def update_texture(self):
        self.tex = 'fence/%s/%s/%s/%s.png' % (self.neighbor_fences[UP],
                                        self.neighbor_fences[RIGHT],
                                        self.neighbor_fences[DOWN],
                                         self.neighbor_fences[LEFT])

@RegisterPersisted
class Flag(Mover):
    def __init__(self, pos, team):
        Entity.__init__(self, pos, ENTITY_SIZE,LAYER_BLOCKS)
        self.tex = team+'_flag.png'
        self.height= ENTITY_SIZE.x

@RegisterPersisted
class Forest:

    def __init__(self, pos_x, pos_y, width, height,edge=2):
        halfwidth = width*0.5
        halfheight = height*0.5
        d_max = sqrt(halfwidth*halfwidth+\
                     halfheight*halfheight)
        for x in range(width):
            for y in range(height):
                if random.random() < 0.025:
                    try:
                        Tree(vector2(pos_x+x, pos_y+y))
                    except CellFull:
                        pass

@RegisterPersisted
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
                        Fruit(vector2(pos_x+x, pos_y+y))
                    except CellFull:
                        pass


@RegisterPersisted
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


