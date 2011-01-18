var DRAW_PERIOD = 100;
var TURN_PERIOD = 500;   
var DRAWS_PER_TURN = TURN_PERIOD/DRAW_PERIOD;

function lerp_frame(first,last){

    return first + (last-first)*(anim_index/DRAWS_PER_TURN);
}



function draw() { 
    var ctxs = {}
    for (var i in canvas_layers) {
        ctxs[i] = canvas_layers[i].getContext("2d");            
        ctxs[i].clearRect(0,0,canvasWidth, canvasHeight);             
    }
    
    for (var ent_id  in new_gamestate.ents)  {

        var ent = new_gamestate.ents[ent_id];
        if (ent.olds && ent.olds['pos']) {
            var x = lerp_frame(ent.olds.pos[0], ent.pos[0]);
            var y = lerp_frame(ent.olds.pos[1], ent.pos[1]);
        } else {
            var x = ent.pos[0];
            var y = ent.pos[1];
        }

        x = entity_size*0.5 + x*entity_size;
        y = entity_size*0.5 + y*entity_size;
    
        var s_x = entity_size*0.5; 
        var s_y = entity_size*0.5;
        var angle = ent.angle;
        var img = new Image();

        if (ent.frames){
            img.src = imageBase+ent.tex+"_"+(anim_index % ent.frames)+".png"; 
        } else {
            img.src = imageBase+ent.tex;
        }
        var ctx = ctxs[ent.layer]; 
        ctx.translate(x,y);
        ctx.rotate(angle);               
        ctx.drawImage(img, -s_x, -s_y, s_x*2, s_y*2);
        ctx.rotate(-angle);
        ctx.translate(-x,-y);   
    }   

    if (anim_index > DRAWS_PER_TURN)
        anim_index = DRAWS_PER_TURN; 
    frame_number += 1;
    anim_index += 1; 
}

//###########################################################
//Message Handlers
//These functions handle messages that come in from the server
//Each message has a type, and the types are dispatched
//to the corresponding message handlers
//############################################################

//top level handler
//dispatches the socket message to the appropriate handler
function socket_message_handler (event) {
	 $('#message').innerHTML = "Update size: " +
	    event.data.length+" bytes.";
	//all messages are just JSON structs
	var message = JSON.parse(event.data);
	//dispatch this message to the appropriate handler
        message_handlers[message.type](message);
}

//This message contains the entire state of the game
//i.e. the position, location &c of all entities
function handle_gamestate(state) {
    new_gamestate = state.state;
}
       
//this message contains changes in the gamestate
//since the last frame. New entities are added,
//dead entities are removed, and states are updated
function handle_delta(delta) {

    for (var id in delta.noobs){
        new_gamestate.ents[id] = delta.noobs[id];
        new_gamestate.ents[id].olds = {};
    }

    
    for (var ent_id in delta.deltas){
        var this_delta = delta.deltas[ent_id];

        for (var att in this_delta){
            ent = new_gamestate.ents[ent_id];
            if (! ent.olds) ent.olds = {};
            ent.olds[att] = ent[att]; 
            ent[att] = this_delta[att];
        }
    }

    for (var i in delta.deads)
        delete new_gamestate.ents[delta.deads[i]];
    anim_index = 0;
}
 
//this message contains game score information   
function handle_score(score_msg) {
    var score_text = '<table class="scores">\n' +
	"<tr><td>Player</td><td>Points</td></tr>"
    var scores = score_msg.scores
    for(var i in scores){
        score_text += "<tr><td>"+
	    scores[i].player + "</td><td> "+scores[i].kills + "</td></tr>\n";
    }  
    $('#scores').innerHTML = score_text;
}

//this function is not in use yet
//but it will be used to cache certain strings
//so that network traffic is minimized
function handle_string_map(map) {
    for (var id in map)
        string_map[id] = map[id]
}
      
/*#######################################################
  Global Variables
########################################################*/
//a description of all the entities in the game
var new_gamestate = {'ents' : {}};
 //used to map strings to ids, to reduce websocket bandwidth
var string_map = {  };
var frame_number = 0;
var anim_index = 0;
//a function dispatch table. Each message that comes in
//has a type, and the type of the message is used to determine
//which handler function should be called
var message_handlers = { 'gs' : handle_gamestate,
			 'delta' : handle_delta,
			 'score' : handle_score};
//the websocket used to communicate with the server
var socket = 0;
//there are multiple canvases so that we can render
//on different layers. 
var canvas_layers = {}
//how big is the canvas?
var canvasWidth = 512;
var canvasHeight = 512;
//how big are individual factory elements?
var entity_size = 16;
//all the images are stored in the same directory
//to save on bandwidth we know to prefix them all with this
var imageBase = '/static/images/';

var player_dir = null;
/*####################################################
  Utility Functions
######################################################*/
//converts a click on the screen to a mouse coordinate
//used for building the factory
function get_cursor_position(e){
    var x;
    var y;
    
    if (e.pageX || e.pageY)  {
        x = e.pageX;
        y = e.pageY;
    } else {
        x = e.clientX  + 
	    document.body.scrollLeft + 
	    document.documentElement.scrollLeft;
        y = e.clientY + 
	    document.body.scrollTop + 
	    document.documentElment.scrollTop;
    }
        
    x -= canvas.offsetLeft;
    y -= canvas.offsetTop;
    x = Math.floor(x / entitySize);
    y = Math.floor(y / entitySize);
    return [x,y]
}


/*#################################################
 Mouse Click handling
 The mouse can be in a number of different states. 
Each state has its own handler function. 
 (This is not implemented yet, but it will be)
#################################################*/
function on_click(e)  {
    return;
}

function on_keydown(e) {
    if (e.which == '37'){
	player_dir = "LEFT";   
    }else if (e.which == '38'){
	player_dir = 'UP';
    }else if (e.which == '39'){
	player_dir = 'RIGHT';
    }else if (e.which == '40'){
	player_dir = 'DOWN';
    }
    if (player_dir)
        socket.send("{ 'dir' : "+player_dir+"}");
    
}


/* #################################################
Main function
###################################################*/
http://dev.gomboloid.com:8000/

function connect()  {       
    socket = new WebSocket("ws://dev.gomboloid.com:8000/ws");

    socket.onmessage = socket_message_handler;
}
function start() {		
    canvas_layers[0] =  $("#layer0")[0];
    canvas_layers[1] =  $("#layer2")[0];
    canvas_layers[2] =  $("#layer2")[0];
    canvas_layers[2].onclick = on_click;
    connect();
    document.onkeydown = on_keydown;
    setInterval("draw()",DRAW_PERIOD);
    
}
    
	
