import tornado
import tornado.ioloop
import tornado.httpserver
import tornado.web
import tornado.websocket
import os
import random
import math
import json

from entities import *
from engine import *
from game import *
from scribit import log, logged, timed

DIRS = { 'LEFT' : LEFT, 'DOWN' : DOWN, 'RIGHT' : RIGHT, 'UP' : UP}
class  MainHandler (tornado.web.RequestHandler):
    def get(self):
      self.render('index.htm')

        
class  JSHandler (tornado.web.RequestHandler):
  def get(self, request):
    self.render('js/'+request+".js")

       
class ImageHandler (tornado.web.RequestHandler):    
  def get(self, imagename):         
    imagename = "images/"+imagename+".png";
    self.write(imagename)

                                

clients_by_name = {}
@RegisterPersisted      
class Client(Updater, Entity):    


    def __init__(self, **kwargs):
        "Creating a new client." 
        log ('Creating a new client object') 
        self.updates =  0 
        self.dir = ZERO_VECTOR 
       
        self.watching = {}
        self.act = None
        self.bomb = None
        self.bomb_cooldown = 0
        self.name = random.choice([ "Chumpalicious",
                                    "Nooborama",
                                    "Wussomatic",
                                    "Llamatastic",
                                    "Failarious"])
        self.death_count = 0
        self.kill_count = 0
        self.disconnected = False
        self.dude = None
        Entity.__init__(self)
        engine.client_manager.add_client(self)
        self.name = kwargs.get('name') or self.id 
        log ("%s joined the game" % self)
        clients_by_name[self.name] = self

    def saves(self, name):
        return name not in { 'socket' : False}

    def __setattr__(self, attr, val):
        self.__dict__[attr] = val

    def get_delta(self):
        return {}

    def __repr__ (self):
        return 'Client %s' % self.id

    def spawn_dude(self, dude=None):
        if not dude:
            log ('spawning dude for %s' % self)
            dude = Player()
        self.dude = dude 
        self.dude.owner = self
        self.dude.on_die = self.handle_player_die
        self.inform_player_of_dude()

    def inform_player_of_dude(self):
        self.send({'type' : 'client_info', 
                    'camera_ent_id' : self.dude.id})


    def follow_dude(self, dude):
        self.following = dude

    def delta_matters(self, delta):
        return len(delta['deltas']) or\
               len(delta['noobs']) or\
                len(delta['deads'])


    def update(self):
        if self.dude == None:
            return

        self.dude.dir = self.dir
        self.dude.act = self.act
        self.dir = ZERO_VECTOR
        self.act = None
        

    def get_neighbor(self, dir):
        t = self.dude.pos + dir*GRID_SIZE
        return engine.metagrid.get_cell(t.x, t.y)

    def send_deltas(self):
        if not self.dude:
            return 
        #check to make sure the guy can see what's around him
        old_watching = {}
        for cell_pos in self.watching:
            old_watching[cell_pos] = True
        #we need to know how the set of what this guy's watching
        #has changed
        newly_watched = {}
        still_watching = {}
        now_watching = {}
        no_longer_watching = {}
        for dir in ALL_DIRS + [ZERO_VECTOR]:
            cell = self.get_neighbor(dir)

            if not cell:
                log ('No cell for direction %s' % dir)
                import pdb
                pdb.set_trace()
            if not cell.get_pos() in old_watching:                
                newly_watched[cell] = cell.get_pos()
            now_watching[cell] = cell.get_pos()

        for cell_pos in old_watching:
            cell = engine.metagrid.get_cell(cell_pos.x, cell_pos.y)
            if not cell in now_watching:
                no_longer_watching[cell] = True 
            else:
                still_watching[cell] = True 
                
        params = (len(now_watching), len(newly_watched),
                  len(still_watching), len(no_longer_watching))

        #do some sanity checks
        for cell in newly_watched:
            if cell in still_watching:
                log("%s was in newly AND still watched!" % 
                            cell)
            if cell in no_longer_watching:
                log("%s was in newly AND no longer watched!" %
                        cell)
        for cell in still_watching:
            if cell in no_longer_watching:
                log("%s was in still and no longer watching!" % cell) 
        #now go through each of these sells and send them 
        #the appropriate message
        for cell in newly_watched:
            #log('now watching %s' % cell)
            if cell and cell.current_state:
                self.send(cell.current_state)
        for cell in still_watching:
            if cell and cell.last_delta and self.delta_matters(cell.last_delta):
                #log('sending delta for %s' % cell)
                self.send(cell.last_delta) 

        for cell in no_longer_watching:
            #log ('no longer watching %s' % cell)
            if cell and cell.drop_message:
                self.send(cell.drop_message)
        
        self.watching = {} 
        for cell in now_watching:
            self.watching[cell.get_pos()] = True


    def handle_player_die(self):
        self.death_count += 1
        if not self.disconnected:
            self.spawn_dude()


    def on_kill(self, victim):
        if victim.owner == self:
            self.kill_count -= 1
        else:
            self.kill_count += 1
            
    def disconnect(self):
        if not self.disconnected:
            self.disconnected = True
            engine.client_manager.remove_client(self)

    #@logged 
    def send(self, message):
        if not self.disconnected\
            and hasattr(self, 'socket'):
            try:
                self.socket.write_message(message)
            except IOError:
                self.disconnect()

    #@logged    
    def on_message(self, message):                        
        msg = json.loads(message)
        if 'dir' in msg:
            self.dir = DIRS[msg['dir']]
        elif 'act' in msg:
            self.act = msg['act']
        elif 'name' in msg:
            self.name = msg['name']
            if self.name in clients_by_name:
                log ('We know this client: ' +self.name)
                client = clients_by_name[self.name] 
                log ('client has dude %s' % client.dude)
                self.spawn_dude(client.dude)
                client.die(self)
                clients_by_name[self.name] = self
            else:
                clients_by_name[self.name] = self
                self.spawn_dude(Player())
            

class SocketConnectionHandler (tornado.websocket.WebSocketHandler):

    def __init__(self, application, request):
        tornado.websocket.WebSocketHandler.__init__(self, application, request)
        """sets up the socket sender""" 
        log ('New client connected: %s' % self.request)
        
    def open(self):
        self.client = Client()
        self.client.socket = self
        self.on_message = self.client.on_message
game = Game()
engine.game = game
engine.build_world()

    
settings = {
"static_path": os.path.join(os.path.dirname(__file__), "static"),
"cookie_secret": "61oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
"login_url": "/login",
"xsrf_cookies": True,
}
application = tornado.web.Application(
    [ (r"/", MainHandler),
      (r"/js/([A-z|0-9]+).js", JSHandler),
      (r'/ws', SocketConnectionHandler, { }),
      (r'/images/([A-z]+).png', ImageHandler)
    
    
    ], **settings)

if __name__ == "__main__":
    log("Starting Tornado web server on port 8000!")
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(8000)
    main_loop = tornado.ioloop.IOLoop.instance();
    scheduler = tornado.ioloop.PeriodicCallback(game.update, TICK_PERIOD, io_loop = main_loop)    
    scheduler2 = tornado.ioloop.PeriodicCallback(engine.save_world,  TICK_PERIOD*100, io_loop = main_loop)    

    scheduler.start()
    scheduler2.start()
    log("Server started, entering main loop.")
    main_loop.start()
