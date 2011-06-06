function lerp_frame(first,last,percent){
    return first + (last-first)*(percent);
}

function lerp_pos(ent){
   
    pieces = [ent.pos.x,ent.pos.y,ent.height] 
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
            pieces[i] = ent.pos[i] + piece;                
            
        }
    }
    if (ent.lerp_targets.height && ent.lerp_frames.height > 0){
        --ent.lerp_frames.height;                
        var how_far = 1 - ent.lerp_frames.pos/DRAWS_PER_TURN;
        how_far = how_far*(ent.lerp_targets.height - ent.height);
        pieces[2] = ent.height + how_far;
            
    }
    
    ent.pos = [pieces[0], pieces[1]];
    ent.height = pieces[2];

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

        lerp_pos(ent);
        x = ent.pos[0];
        y = ent.pos[1];

        x = canvas_width/2 + entity_size*(ent.pos[0]+0.5)
        y = canvas_height/2 + entity_size*(ent.pos[1]+ 0.5 - ent.height);

    
        return [x,y,ent.height, cx, cy];
}

function render_image(ctx,x,y,h,angle,img,s_x,s_y,scale){
        ctx.translate(x,y-h);
        ctx.rotate(angle);               
        ctx.scale(scale,scale);
        ctx.drawImage(img, -s_x, -s_y)
        ctx.scale(1.0/scale,1.0/scale);
        ctx.rotate(-angle);
        ctx.translate(-x,-(y-h))
}
var animations = {

    'base' : function(contexts, ent) {


        pos = get_entity_pos(ent);
        var x = pos[0];
        var y = pos[1];
        var h = pos[2];
        
        var s_x =   ent.size[0]; 
        var s_y = ent.size[1];
        var angle = ent.angle;
        var img = new Image();
        img.src = image_base + ent.tex;
        render_image(contexts[ent.layer],x,y,h,angle,img,s_x,s_y,base_scale);
;
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

        if (walking){
            ent.frame =  (ent.frame+1) % 3;
        }

        img.src = image_base + ent.tex+"/"+ent.frame+".png";
        
        var ctx = contexts[ent.layer]
        render_image(ctx,x,y,h,angle,img,s_x,s_y,base_scale);
    } 


};
