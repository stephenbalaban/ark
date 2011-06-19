import random
from vector2  import *
from metagrid import GRID_SIZE, METAGRID_SIZE

ENTITY_SIZE = vector2(8,8)

entity_class_registry = {}
def RegisterPersisted(f):
    entity_class_registry[f.__name__] = f
    return f

   
@RegisterPersisted
class PersistedWrapper:

    def __init__(self, target_id):
        self.id = target_id
        self.target = None

    def __getattr__(self, name):

        if name == 'id' :
            return self.id
        if  not self.target:
            #see if you can get the entity from the database
            print 'getting entity', self.id
            self.target = engine.get_entity(self.id)

        if not self.target:
            raise NoSuchEntity("Empty json wrapper for '%s'" % self.id)
        return getattr(self.target, name)
        
class Persisted:
    def dump_json(self):
        res = {}
        vars_to_save = [name 
                            for name 
                            in self.__dict__
                            if self.saves(name)]
        for varname in vars_to_save:
            val = self.__dict__[varname]
            if not (inspect.isfunction(val) or\
                    inspect.ismethod(val) or\
                    inspect.isclass(val)) :
                res[varname] = val
        res['__class__'] = self.__class__.__name__ 
        return res 

    def persist(self, datastore):
        ent_data = self.dump_json()
        #constructors set these up
        del ent_data['net_vars']
        ent_data['_id'] = self.id
        try:
            datastore.entities.save(ent_data,manipulate=True,safe=True) 
        except Exception, exc:
            import pdb
            log ('Exception : %s' % exc )
            pdb.set_trace()

    def saves(self, name):
        return True

 
class Entity(Persisted):
    "abstract base class for things in the game"
    def __init__(self,**params ):

        self.__dict__['net_vars'] = {
                 'tex': True,
                 'angle' : True,
                 'size' :True,
                 'scale' : True,
                 'pos' : True,
                 'layer' : True,
                 'height': 0,
                 'id' : -1,
                 'lerp_targets' : {},
                 'lerp_frames' : {},
                 'frame' : 0
                }           


        self.__dict__["delta"] = {}
        
    
        self.id = params.get('id') or make_entity_id()      
        self.tex = params.get('tex') or 'none.png'
        self.dead = False
        self.pos = params.get('pos') or None 
        if self.pos:
            self.pos.x = self.pos.x % (GRID_SIZE*METAGRID_SIZE)
            self.pos.y = self.pos.y % (GRID_SIZE*METAGRID_SIZE)
        self.size = params.get('size') or ENTITY_SIZE 
        self.dir =  params.get('dir') or RIGHT 
        self.angle = params.get('angle') or 0 
        self.layer = params.get('layer') or 0 
        self.height = params.get('height') or 0
        self.scale = params.get('scale') or 1
        self.lerp_targets = {}
        self.lerp_frames = {}
        self.frame = params.get('frame') or 0 
        
        special_keys = ['__class__']
        for param in params:
            if not param in special_keys: 
                setattr(self, param, params[param])
        from engine import engine
        engine.add_entity(self)
    


    def __repr__(self):
        start = "%s %s"  % (self.__class__.__name__,
                                self.id or "No id")
        if self.pos:
            return start + ' at %s, %s, %s' % (self.pos.x ,
                                         self.pos.y, self.layer)
        return start

  
    def __setattr__(self, attr_name, value):

        if attr_name in self.net_vars:
            if attr_name in self.__dict__:
                if self.__dict__[attr_name] == value:
                    return 
            self.delta[attr_name] = value
        self.__dict__[attr_name] =  value

    def move(self, new_pos):
        from engine import engine
        x,y = engine.metagrid.wrap_coords(new_pos.x, new_pos.y)
        new_pos = vector2(x,y)
        engine.metagrid.move_entity(self,new_pos)
    
    def update(self):
        pass 
      
    
    def change_tex(self, new_tex):
        self.tex = new_tex

    def change_size(self, new_size):
        self.size  = new_size

    def die(self, killer=None):
        from engine import engine
        engine.remove_entity(self,moving=False)
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
                
class NoSuchEntity: 
    def __init__(self, msg):
        self.message = msg


class Updater: pass

ID_CHARS = [chr(x) for x in range(256) 
                if (chr(x).isalpha() or chr(x).isdigit())]


def make_entity_id():
            return ''.join([random.choice(ID_CHARS) 
                            for x in range(8)])
 
