import tornado.httpserver
import tornado.ioloop
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

                                


            
class Client:    


    def __init__(self, socket):
        "Creating a new client." 
        self.updates =  0 
        self.socket = socket        
        self.dir = ZERO_VECTOR 
        socket.on_message = self.on_message
       
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
        self.id = engine.make_id() 
        self.dude = None
        log ("%s joined the game" % self)
        engine.add_client(self)

    def __repr__ (self):
        return 'Client %s' % self.id

    def spawn_dude(self):
        self.dude = Dude(self)
        self.dude.on_die = self.handle_player_die
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
  
        self._send_deltas()
        self.dude.dir = self.dir
        self.dude.act = self.act
        self.dir = ZERO_VECTOR
        self.act = None
        
    def _send_deltas(self):
        #check to make sure the guy can see what's around him
        now_watching = {}
        #we need to know how the set of what this guy's watching
        #has changed
        newly_watched = {}
        still_watching = {}
        no_longer_watching = {}
        for dir in ALL_DIRS + [ZERO_VECTOR]:
            t = self.dude.pos+dir*GRID_SIZE
            cell = engine.metagrid.get_cell(t.x, t.y)
            if not cell in self.watching:                
                newly_watched[cell] = True
            now_watching[cell] = True

        for cell in self.watching:
            if not cell in now_watching:
                no_longer_watching[cell] = True
            else:
                still_watching[cell] = True
                
        params = (len(now_watching), len(newly_watched),
                  len(still_watching), len(no_longer_watching))
        #log("%d now watched. %d new, %d still, %d no longer" % params)

        #do some sanity checks
        for cell in newly_watched:
            if cell in still_watching:
                log_error("%s was in newly AND still watched!" % 
                            cell)
            if cell in no_longer_watching:
                log_error ("%s was in newly AND no longer watched!" %
                        cell)
        for cell in still_watching:
            if cell in no_longer_watching:
                log_error("%s was in still and no longer watching!" % cell) 
        #now go through each of these sells and send them 
        #the appropriate message
        for cell in newly_watched:
            if cell.current_state:
                self.send(cell.current_state)
        for cell in still_watching:
            if cell.last_delta and self.delta_matters(cell.last_delta):
                self.send(cell.last_delta) 
        for cell in no_longer_watching:
            if cell.drop_message:
                self.send(cell.drop_message)

        
        self.watching = now_watching


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
        self.disconnected = True
        if self.dude:
            self.dude.die(self)

    #@logged 
    def send(self, message):
        self.socket.write_message(message)

    @logged    
    def on_message(self, message):                        
        msg = json.loads(message)
        if 'dir' in msg:
            self.dir = DIRS[msg['dir']]
        elif 'act' in msg:
            self.act = msg['act']
        elif 'name' in msg:
            self.name = msg['name']

 
class SocketConnectionHandler (tornado.websocket.WebSocketHandler):

    def __init__(self, application, request):
        tornado.websocket.WebSocketHandler.__init__(self, application, request)
        """sets up the socket sender""" 
        self.client = Client(self)
        
    def open(self):
        print "Client",self.client.id," opened a socket. They are alive!"
        self.client.spawn_dude()

game = Game()
game.make_maze()


    
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
    print "Starting Tornado web server on port 8000!";
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(8000)
    main_loop = tornado.ioloop.IOLoop.instance();
    scheduler = tornado.ioloop.PeriodicCallback(game.update, TICK_PERIOD, io_loop = main_loop)    
    scheduler.start()
    print "Server started, entering main loop."
    main_loop.start()
