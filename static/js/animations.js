function lerp_frame(first,last,percent){
    return first + (last-first)*(percent);
}

function get_entity_pos(ent){

        var old_ent = ent;
        if (ent.id in old_gamestate.ents)
            old_ent = old_gamestate.ents[ent.id];
        if (camera_ent_id == -1){            
            var cam = { 'pos' : [0,0]};
            var old_cam = {'pos' : [0,0]};
        }

        else{
            var cam = new_gamestate.ents[camera_ent_id];
            var old_cam = old_gamestate.ents[camera_ent_id];

            if (! cam)
                cam = {'pos' : [0,0]}
            if (! old_cam){
                if (cam)
                    old_cam = {'pos' : cam.pos}
                else{
                    old_cam = {'pos' : [0,0]}
                }

            }
        }
        var cx = cam.pos[0];
        var cy = cam.pos[1];
        var ocx = old_cam.pos[0];
        var ocy = old_cam.pos[1];
        var x = lerp_frame(old_ent.pos[0] - ocx, ent.pos[0] - cx, lerp_frac);
        var y = lerp_frame(old_ent.pos[1] - ocy, ent.pos[1] - cy, lerp_frac);
        var h = lerp_frame(old_ent.height, ent.height, lerp_frac);
 
        x = canvas_width/2 + entity_size*(x+0.5)
        y = canvas_height/2 + entity_size*(y + 0.5)
    
        return [x,y,h, cx, cy];
}
var animations = {

    'base' : function(contexts, ent) {


        pos = get_entity_pos(ent);
        var x = pos[0];
        var y = pos[1];
        var h = pos[2];
        
    

        var s_x = ent.size[0]; 
        var s_y = ent.size[1];
        var angle = ent.angle;
        var img = new Image();
    img.src = image_base + ent.tex;

    var ctx = contexts[ent.layer]
        ctx.translate(x,y-h);
        ctx.rotate(angle);               
        ctx.drawImage(img, -s_x, -s_y)
        ctx.rotate(-angle);
        ctx.translate(-x,-(y-h));
    },

    'dude' : function(contexts, ent) {

    
    
        pos = get_entity_pos(ent);
        var x = pos[0];
        var y = pos[1]
        var h = pos[2];
        var cx = pos[3];
        var cy = pos[4];
        
        var walking =  (ent.id in old_gamestate.ents &&
                old_gamestate.ents[ent.id].pos != ent.pos &&
                draw_frame_number - new_gamestate.draw_frame <= DRAWS_PER_TURN);
        var s_x = ent.size[0]; 
        var s_y = ent.size[1];
        var angle = ent.angle;
        var img = new Image();

    if (! ent.frame)
        ent.frame = 0;
    if (walking){
            ent.frame =  (ent.frame+1) % 3;
    }

        img.src = image_base + ent.tex+ent.frame+".png";

    var ctx = contexts[ent.layer]
        ctx.translate(x,y-h);
        ctx.rotate(angle);               
        ctx.drawImage(img, -s_x, -s_y)
        ctx.rotate(-angle);
        ctx.translate(-x,-y+h);
    } 


};
