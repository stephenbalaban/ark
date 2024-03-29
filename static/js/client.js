
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
var entity_size = 32;
var camera_ent_id = -1;
var base_scale = entity_size/16;
var grid_size = 8*4;
//all the images are stored in the same directory
//to save on bandwidth we know to prefix them all with this
var image_base = '/static/images/';

var old_ticks = old_gamestate.ticks;
var new_ticks = new_gamestate.ticks;

var gamestate_buffer = {old_ticks: old_gamestate,
                        new_ticks: new_gamestate};

var TURN_PERIOD = 250;   
var DRAWS_PER_TURN = 6;
var DRAW_PERIOD = 100
var SERVER_ADDRESS = "localhost:8000";
var draw_frame_number = 0;
var game_frame_number = 0;
var global_anim_index = 0;
var game_frame_start = 0;
var last_delta = {'deltas' : {}};
var pending_deltas = []
var lerp_frac = 0.0;
var total_bytes = 0;
var bw_start_frame = 0;
var ping_period = 10;
var entity_count = 0;
/*####################################################
 * Animation code
 * ##################################################*/
function draw() { 
    var contexts = {}

    for (var i in canvas_layers) {
        contexts[i] = canvas_layers[i].getContext("2d");            
        contexts[i].clearRect(0,0,canvas_width, canvas_height);   
    }
    //this is the position of the camera in the game world
    //entities are drawn relative to the camera
    //
    
    var update_message = ""; 
    for (var msg_type in message_counts){
        update_message += msg_type+": "+message_counts[msg_type];
        update_message += "<br>";
    }

    
    update_message += "Entities: "+entity_count+"<bar>";

    //$("#messages").html(update_message);
    //
    for (var ent_id  in new_gamestate.ents)  {
        var ent = new_gamestate.ents[ent_id];
        
        if (ent.lerp_targets.pos && ent.lerp_frames.pos > 0){
            --ent.lerp_frames.pos;                
            var how_far = 1 - ent.lerp_frames.pos/DRAWS_PER_TURN;
            for (var i in [0,1]){
                var piece = (ent.lerp_targets.pos[i] - ent.pos[i]) 

                while (piece > grid_size/2)
                    piece -= grid_size;
                while (piece < -grid_size/2)
                    piece += grid_size;

                piece = piece * how_far;
                ent.pos[i] += piece;                

                
            }
        }
        if (ent.lerp_targets.height && ent.lerp_frames.height > 0){
            --ent.lerp_frames.height;                
            var how_far = 1 - ent.lerp_frames.pos/DRAWS_PER_TURN;
            how_far = how_far*(ent.lerp_targets.height - ent.height);
            ent.height += how_far;
                
        }
    }

    for (var ent_id in new_gamestate.ents){
        var ent = new_gamestate.ents[ent_id];

       
        if (ent.anim && ent.anim in animations){
            animations[ent.anim](contexts, ent);
        } else {
            animations.base(contexts, ent)
        }
    }  
    draw_frame_number += 1;
    
    if (draw_frame_number % 10 == 0){

        $("#debug_bandwidth").html(total_bytes/(1024/4)+' kbps')
        total_bytes = 0;
    }
    

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
    total_bytes = total_bytes + event.data.length;
    var message = JSON.parse(event.data);
    //dispatch this message to the appropriate handler
        message_handlers[message.type](message);
        ++message_counts[message.type];
}

//This message contains the entire state of the game
//i.e. the position, location &c of all entities
function handle_gamestate(state) {
    for (var ent_id in state.state.ents) {
        new_gamestate.ents[ent_id] = state.state.ents[ent_id];
    }
    new_gamestate.draw_frame = draw_frame_number + DRAWS_PER_TURN;
    game_frame_number = state.frame;
}
       
//this message contains changes in the gamestate
//since the last frame. New entities are added,
//dead entities are removed, and states are updated
function handle_delta(delta) {
    apply_delta(delta, new_gamestate);
}


    
function apply_delta(delta, gamestate){
    for (var id in delta.noobs){
        gamestate.ents[id] = delta.noobs[id];
        gamestate.ents[id].olds = {};
        ++entity_count;
    }
    
    for (var ent_id in delta.deltas){
        var this_delta = delta.deltas[ent_id];

        ent = gamestate.ents[ent_id];
        if (typeof ent === 'undefined')
            continue;
        for (var att in this_delta){
            if (att == 'pos' || att == 'height'){
                ent.lerp_targets[att] = this_delta[att];
                ent.lerp_frames[att] = DRAWS_PER_TURN;
            }else{
                ent[att] = this_delta[att];
            }
        }
    }


    for (var i in delta.deads){
        delete gamestate.ents[delta.deads[i]];
        --entity_count;
    }
   gamestate.ticks = delta.frame;
}   


function handle_client_info(info){
    camera_ent_id = info.camera_ent_id;
} 

function handle_drop(drop){
    for (var index in drop.ents){
        delete new_gamestate.ents[drop.ents[index]];
        --entity_count;
    }
}
//a function dispatch table. Each message that comes in
//has a type, and the type of the message is used to determine
//which handler function should be called
var message_handlers = { 'gs' : handle_gamestate,
             'delta' : handle_delta,
             'score' : handle_score,
            'client_info' : handle_client_info,
            'drop' : handle_drop};

var message_counts = { 'gs' : 0,
                        'delta' : 0,
                        'score' :0,
                        'client_info' : 0,
                        'drop' : 0};

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

    }else if (e.which == '32'){
        msg['act'] = 'use';
    }else if (e.which == '88'){
        msg['act'] = 'shoot';
    }


    if (socket)
        socket.send(JSON.stringify(msg));
    
}


/* #################################################
Main function
###################################################*/

function connect()  {       
    socket = new WebSocket("ws://"+SERVER_ADDRESS+"/ws");
    socket.onmessage = socket_message_handler;
    socket.onopen = function () {
        socket.send(JSON.stringify({"name" : $("#input_box").val()}));

    };
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
        
  $("#content").append("<div id=\"input_box_area\""+
                             ">");

    $("#input_box_area").append('<input type="text" id="input_box"/>');
    $("#input_box_area").append('<input type="button" id="input_button" value="connect"/>');

    $("#input_button").click(function (clickEvent) {
            new_gamestate = {'ents' : {}, 'ticks' : 0, 'draw_frame' : 0};
            connect();
            return false;
        });
    
    document.onkeydown = on_keydown;
    setInterval("draw()",DRAW_PERIOD);
    
}
    
    
