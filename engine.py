import random
from vector2 import *

TICK_PERIOD = 250
UP = vector2(0,-1)
DOWN = vector2(0,1)
LEFT = vector2(-1,0)
RIGHT = vector2(1,0)
ENTITY_SIZE = vector2(8,8)
GRID_SIZE = 32

class ClientManager:
    
    def __init__(self):
        self.clients = {}
        self.next_client_id = 0
        
    def add_client(self,client):
        self.next_client_id += 1;
        self.clients[self.next_client_id] = client
        client.id = self.next_client_id
              
    def broadcast(self, message):
        #some clients have disconnected
        #keep track of this
        new_clients = {}                                       
        for id in self.clients:
            try:            
                self.clients[id].send(message)
                new_clients[id] = self.clients[id]
            except IOError, e:
                print "client",id,"disconnected."
                self.clients[id].disconnect()
        self.clients = new_clients

class GridCell:
	
	def __init__(self, num_layers):

		self.entities = {}

	def get_entities(self):
		ents = {}
		for layer in self.entities:
			ent = self.entities[layer]
			ents[layer] = ent
		return ents

	def add_entity(self, ent):
		"Tries to add the entity. Returns false if "\
		"that layer is full."
		if ent.layer in self.entities:
			print "couldn't add ",ent
			return False
		self.entities[ent.layer] = ent
		return True

	def remove_entity(self, ent):

		if ent.layer in self.entities:
				
			other = self.entities.pop(ent.layer)
			print "removed a", other
			return True
		else:
			return False	

				

		


class GameGrid:

	def __init__(self, num_layers, size):

		self.cells =  [[ GridCell(num_layers)
						 for  y in range(size)]
									for x in range(size)]
		self.size = size

	def get_entities(self, x, y):

		if x < 0 or x >= self.size or \
		   y < 0 or y >= self.size:
			return {}
		else:
			return self.cells[x][y].get_entities()


	def add_entity(self, ent):
		if ent.pos.x < 0 or ent.pos.x >= self.size or \
		   ent.pos.y < 0 or ent.pos.y >= self.size:
			return False
		else:
			return self.cells[ent.pos.x][ent.pos.y].add_entity(ent)

	def remove_entity(self, ent):
		if ent.pos.x < 0 or ent.pos.x >= self.size or \
		   ent.pos.y < 0 or ent.pos.y >= self.size:
			return False
		else:
			return self.cells[ent.pos.x][ent.pos.y].remove_entity(ent)

 


class Engine:
    """encapsulates the behavior of the entire game"""
    
    def __init__(self):
        self.client_manager = ClientManager()        
        self.dude_map = {}
        self.next_id = 0
        self.noobs = []
        self.current_frame = 0
        self.grid = GameGrid(4, 256)

    def set_game(self, game):
        "Sets self.game. Game entitie can use " \
        "this property to mess with the game as a whole. "
        self.game = game
        
    def add_client(self, client):
        #add this guy to the list of clients
        self.client_manager.add_client(client)
        
    
    def add_entity(self, entity):
        self.next_id += 1
        self.noobs += [entity]
        entity.id = self.next_id

    def add_noobs(self):
		noob_map = {}
		for noob in self.noobs:
			print "adding",noob
			self.dude_map[noob.id] = noob
			noob_map[noob.id] = noob.get_state()
			if not self.grid.add_entity(noob):
				print ("Couldn't add %s at "\
					  "(%0.3f, %03.f) to grid.") % (noob.__class__,
													noob.pos.x,
                                                noob.pos.y)

		self.noobs = []
		return noob_map

   
    def get_entities_in_radius(self, pos, radius):

        results = []
        for id in self.dude_map:
            ent = self.dude_map[id]
            delta = (ent.pos - pos).length()
            if delta < ent.size.length() + radius:
                results += [ent]
        return results


    def remove_entity(self, entity):
        self.dude_map[entity.id] = None
    
    def update_entity_map(self):
        # prune out the dead entities by building a new entity map
        
        new_map = {}
        deads = []
        for id in self.dude_map:
            entity = self.dude_map[id]
            if (entity):
                new_map[id] = entity
            else:
                deads += [id]
        self.dude_map = new_map
        noobs = self.add_noobs()
        self.current_frame += 1

        return noobs, deads
 
              
        
    def update(self):
        
        noobs, deads = self.update_entity_map()
        delta_list = {'type' : 'delta',
              'noobs' : noobs,
              'deads' : deads, 
                      'deltas': {}}
        gamestate = { 'type' : 'gs',
                      'ents' : {}}
        for client_id in self.client_manager.clients:
            client = self.client_manager.clients[client_id]
            client.update()
        for ent_id in self.dude_map:
            entity = self.dude_map[ent_id]
            if entity:
                entity.update()
                delta = entity.get_delta()
                if delta:
                    delta_list['deltas'][entity.id] = entity.get_delta()
                if entity.tex:
                    gamestate['ents'][entity.id] = entity.get_state()
                
    
        self.current_state = { 'type' : 'gs',
                               'state' : gamestate }
        
        #tell everyone about the current gamestate
        #but don't bother if there are no changes
	if len(delta_list['deltas']) !=  0 \
	or len(delta_list['noobs']) != 0 \
	or len(delta_list['deads']) != 0:
            self.client_manager.broadcast(delta_list)
        

    
engine = Engine()



class Entity:
	"abstract base class for things in the game"
	def __init__(self, pos, size):
		self.tex = 'none.png'
		self.dead = False
		self.pos = pos
		self.size = size;
		self.pos_changed = False
		self.img_changed = False
		self.size_changed = False
		self.layer = 0
		self.frames = 0
		self.angle = 0 
		engine.add_entity(self)

	def move(self, new_pos):
		engine.grid.remove_entity(self)
		self.pos = new_pos
		self.pos_changed = True
		engine.grid.add_entity(self)
		
	def change_tex(self, new_tex):
		self.tex = new_tex
		self.img_changed = True

	def change_size(self, new_size):
		self.size  = new_size
		self.size_changed = True

	def die(self, killer=None):
		engine.remove_entity(self)
		self.dead = True

	def get_state(self):

			return {'pos': (self.pos.x, self.pos.y),
			'size': (self.size.x, self.size.y),
			'tex': self.tex,
			'layer': self.layer,
			'frames' : self.frames,
			'angle' : self.angle}

	def get_delta(self):
		delta = {}
		if self.pos_changed:
			delta['pos'] = (self.pos.x, self.pos.y)
		if self.img_changed:
			delta['tex'] = self.tex
		if self.size_changed:
			delta['size'] = self.size
		if len(delta) == 0:
			return None
		return delta
		
   
