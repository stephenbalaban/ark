
/*#######################################################
  Global Variables
########################################################*/
//a description of all the entities in the game
var old_gamestate = {'ents' : {}, 'ticks' : -1, 'draw_frame' : -1};
var new_gamestate = {'ents' : {}, 'ticks' : 0, 'draw_frame' : 0};
 //used to map strings to ids, to reduce websocket bandwidth
var string_map = {  };

//the websocket used to communicate with the server
var socket = 0;
//there are multiple canvases so that we can render
//on different layers. 
var canvas_layers = {}
//how big is the canvas?
var canvas_width = 400;
var canvas_height = 400;
var entity_size = 16;
var camera_ent_id = -1;
//all the images are stored in the same directory
//to save on bandwidth we know to prefix them all with this
var image_base = '/static/images/';

var old_ticks = old_gamestate.ticks;
var new_ticks = new_gamestate.ticks;

var gamestate_buffer = {old_ticks: old_gamestate,
                        new_ticks: new_gamestate};

var TURN_PERIOD = 250;   
var DRAWS_PER_TURN = 4;
var DRAW_PERIOD = TURN_PERIOD/DRAWS_PER_TURN;
var SERVER_ADDRESS = "dev.gomboloid.com:8000";
var draw_frame_number = 0;
var game_frame_number = 0;
var global_anim_index = 0;
var game_frame_start = 0;
var last_delta = {'deltas' : {}};
var pending_deltas = []
var lerp_frac = 0.0;
/*####################################################
 * Animation code
 * ##################################################*/
function draw() { 
    var contexts = {}
    var lerp_time = new_gamestate.draw_frame - old_gamestate.draw_frame;
    lerp_frac = (draw_frame_number - old_gamestate.draw_frame)/DRAWS_PER_TURN;
    
    if (lerp_frac > 1){
        lerp_frac = 1;
        var got_one = false;
        while (pending_deltas.length > 0) {
            apply_delta(pending_deltas.pop(), old_gamestate);
            got_one = true;
        }
        old_gamestate.draw_frame= draw_frame_number;

    }
   $("#messages").html(lerp_frac); 

    for (var i in canvas_layers) {
        contexts[i] = canvas_layers[i].getContext("2d");            
        contexts[i].clearRect(0,0,canvas_width, canvas_height);             
    }
    //this is the position of the camera in the game world
    //entities are drawn relative to the camera
 
    for (var ent_id  in new_gamestate.ents)  {

        var ent = new_gamestate.ents[ent_id];

       
        if (ent.anim && ent.anim in animations){
            animations[ent.anim](contexts, ent);
        } else {
            animations.base(contexts, ent)
        }
    }  
    draw_frame_number += 1;

    
        

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
    //all messages are just JSON structs
    var message = JSON.parse(event.data);
    //dispatch this message to the appropriate handler
        message_handlers[message.type](message);
}

//This message contains the entire state of the game
//i.e. the position, location &c of all entities
function handle_gamestate(state) {
    new_gamestate = state.state;
    old_gamestate = JSON.parse(JSON.stringify(state.state));
    new_gamestate.draw_frame = draw_frame_number + DRAWS_PER_TURN;
    old_gamestate.draw_frame = draw_frame_number;
    game_frame_number = state.frame;
}
       
//this message contains changes in the gamestate
//since the last frame. New entities are added,
//dead entities are removed, and states are updated
function handle_delta(delta) {
    apply_delta(delta, new_gamestate);
    new_gamestate.draw_frame = draw_frame_number+DRAWS_PER_TURN;
    pending_deltas.unshift(JSON.parse(JSON.stringify(delta)));
}


    
function apply_delta(delta, gamestate){
    for (var id in delta.noobs){
        gamestate.ents[id] = delta.noobs[id];
        gamestate.ents[id].olds = {};
    }
    
    for (var ent_id in delta.deltas){
        var this_delta = delta.deltas[ent_id];

        ent = gamestate.ents[ent_id];
        for (var att in this_delta)
            ent[att] = this_delta[att];
    }

    for (var i in delta.deads)
        delete gamestate.ents[delta.deads[i]];
   gamestate.ticks = delta.frame;
}   


function handle_client_info(info){
    camera_ent_id = info.camera_ent_id;
} 
//a function dispatch table. Each message that comes in
//has a type, and the type of the message is used to determine
//which handler function should be called
var message_handlers = { 'gs' : handle_gamestate,
             'delta' : handle_delta,
             'score' : handle_score,
            'client_info' : handle_client_info};
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

function log_message(msg){

    var so_far = $("#log").html()+"<br>";
    $("#log").html(so_far+msg);

}
/*#################################################
 Mouse Click handling
 The mouse can be in a number of different states. 
Each state has its own handler function. 
 (This is not implemented yet, but it will be)
################################       if (ent.olds.pos != ent.pos)#################*/
function on_click(e)  {
    return;
}

function on_keydown(e) {

    msg = {}
    if (e.which == '37'){
        msg['dir'] = "LEFT";   
    }else if (e.which == '38'){
        msg['dir'] = 'UP';
    }else if (e.which == '39'){
        msg['dir'] = 'RIGHT';
    }else if (e.which == '40'){
        msg['dir'] = 'DOWN';

    }else if (e.which = '32'){
        msg['act'] = 'use';
    }

    socket.send(JSON.stringify(msg));
    
}


/* #################################################
Main function
###################################################*/

function connect()  {       
    socket = new WebSocket("ws://"+SERVER_ADDRESS+"/ws");
    socket.onmessage = socket_message_handler;
}
function start() {      

    $("#canvasses").css({"width" : canvas_width,
                         "height" : canvas_height});
    for (var i =0; i < 5; ++i){
        var id = "layer_"+i.toString();
        var canvas_id = id+"_canvas";

        $("#canvasses").append("<div class=\"canvas_layer\"" +
                            "id=\""+id+"\"></div>");

        $("#"+id).css({ "id" : id,
                    "class" : "canvas_layer",
                    "position" : "relative",
                    "top" : -(i)*canvas_height+"px",
                    "padding" : 0,
                    "margin" : "0% auto",
                    "left" : 0,
                    "z-index" : i,
                    "width" : canvas_width+"px",
                    "height" : canvas_height+"px",
        }); 
    
        $("#"+id).append("<canvas id=\""+canvas_id+"\" "+
                         "width=\""+canvas_width+"\" " +
                         "height=\""+canvas_height+"\"/>");
        canvas_layers[i] = $("#"+canvas_id)[0];
    }
    
    $("#canvasses").css({"width" : canvas_width+"px",
                        "height" : canvas_height+"px"});
        
    
    
    connect();
    document.onkeydown = on_keydown;
    setInterval("draw()",DRAW_PERIOD);
    
}
    
    
