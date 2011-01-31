from engine import Engine
from vector2 import vector2


class Entity:
    "abstract base class for things in the game"
    def __init__(self, pos, size, layer=0):
	global engine
        self.__dict__['net_vars'] = {
                 'tex': True,
                 'angle' : True,
                 'size' :True,
                 'pos' : True,
                  'layer' : True,
                 'height': 0,
                 'id' : -1,
                 'targets' : {},
                  'lerp_ticks' : {},
                }           


        self.__dict__["delta"] = {}
        
    
            
        self.tex = 'none.png'
        self.dead = False
        self.pos = pos
        self.size = size
        self.dir = ZERO_VECTOR
        self.angle = 0
        self.layer = layer 
        self.height = 0
        self.targets = {}
        self.lerp_ticks = {}
        engine.add_entity(self)

    def __setattr__(self, attr_name, value):

        if attr_name in self.net_vars:
            if attr_name in self.__dict__:
                if self.__dict__[attr_name] == value:
                    return 
            self.delta[attr_name] = value
        self.__dict__[attr_name] =  value

    def move(self, new_pos):
        engine.grid.remove_entity(self)
        self.pos = new_pos
        engine.grid.add_entity(self)
    
    def update(self):
        pass 
        
    def change_tex(self, new_tex):
        self.tex = new_tex

    def change_size(self, new_size):
        self.size  = new_size

    def die(self, killer=None):
        engine.remove_entity(self)
        self.dead = True

    def get_state(self):

        state = {}
        for varname in self.net_vars:
            val = self.__dict__[varname]
            if hasattr(val, 'to_json'):
                val = val.to_json()
            state[varname] = val
        return state

    def get_delta(self):
        out_delta = {}
        #do json encoding here
        for varname in self.delta:
            val = self.delta[varname]
            if hasattr(val,'to_json'):
                val = val.to_json()
            out_delta[varname] = val
        self.delta = {}
        return out_delta
                

