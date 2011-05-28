from engine import Engine, Mover

class Dude(Mover):

    def __init__(self,owner):

        pos = engine.grid.get_free_position(LAYER_BLOCKS)

        Entity.__init__(self, pos, ENTITY_SIZE, LAYER_BLOCKS )

        self.net_vars['anim'] = True
        self.height = ENTITY_SIZE.x*0.5;
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
                if self.try_move(self.dir):
                    if self.carrying:
                        self.carrying.pos = self.pos
            self.last_dir = self.dir
        elif self.act == 'use':
            self.state = 'using'
            self.use()
        else:
            self.state = 'standing'
        self.update_texture()
         

    def use(self):
        

        if self.carrying:
            
            target_pos = self.pos + self.last_dir
            dudes = engine.grid.get_entities(target_pos.x, target_pos.y)

           
            if not LAYER_BLOCKS in dudes:

                if LAYER_GROUND_DETAIL in dudes:
                    ent = dudes[LAYER_GROUND_DETAIL]
                    if isinstance(ent, PlowedPatch):
                        if ent.state == 'unplanted':
                            self.carrying.pos = ent.pos
                            ent.plant(self.carrying)
                            self.carrying.carried_by = None
                            self.carrying.height = 0.5
                            self.carrying = None
                            return
                else:
                    print "can plant"
                    self.carrying.pos = target_pos
                    engine.grid.add_entity(self.carrying)
                    self.carrying.carried_by = None
                    self.carrying.height = ENTITY_SIZE.x*0.5
                    self.carrying = None
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
                    other_guy.height = ENTITY_SIZE.x*2.5
                    self.carrying = other_guy
                    other_guy.pos = self.pos
            elif not LAYER_GROUND_DETAIL in dudes:
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
                
