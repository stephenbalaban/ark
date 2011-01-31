function lerp_frame(first,last,percent){
    return first + (last-first)*(percent);
}

function get_entity_pos(ent){

        if (camera_ent_id == -1){            
            var cam = { 'pos' : [0,0]};
        }

        else{
            var cam = new_gamestate.ents[camera_ent_id];
            if (! cam)
                cam = {'pos' : [0,0]}
        }



        var cx = cam.pos[0];
        var cy = cam.pos[1];
        var x = ent.pos[0];
        var y = ent.pos[1];
        var height = ent.height;

        x = canvas_width/2 + entity_size*(x-cx+0.5)
        y = canvas_height/2 + entity_size*(y-cy + 0.5) - height;
    
        return [x,y,height, cx, cy];
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



        var walking = false;
        if (ent.lerp_frames.pos && ent.lerp_frames.pos >0 )
            walking = true;
      
                
        var s_x = ent.size[0]; 
        var s_y = ent.size[1];
        var angle = ent.angle;
        var img = new Image();

    if (! ent.frame)
        ent.frame = 0;
    if (walking){
            ent.frame =  (ent.frame+1) % 3;
    }

        img.src = image_base + ent.tex+"/"+ent.frame+".png";

    var ctx = contexts[ent.layer]
        ctx.translate(x,y-h);
        ctx.rotate(angle);               
        ctx.drawImage(img, -s_x, -s_y)
        ctx.rotate(-angle);
        ctx.translate(-x,-y+h);
    } 


};
