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
        var dx = x - cx;
        var dy = y - cy;

        while (dx > grid_size/2)
           dx -= grid_size;
        while (dx < -grid_size/2)
           dx += grid_size;

        while (dy > grid_size/2)
            dy -= grid_size;
        while (dy < -grid_size/2)
           dy += grid_size;



        var height = ent.height;

        x = canvas_width/2 + entity_size*(dx+0.5);
        y = canvas_height/2 + entity_size*(dy + 0.5) - height;
    
        return [x,y,height, cx, cy];
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
        render_image(contexts[ent.layer],x,y,h,angle,img,s_x,s_y,base_scale*ent.scale);
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
        var heart = new Image()

        if (walking){
            ent.frame =  (ent.frame+1) % 3;
        }

        img.src = image_base + ent.tex+"/"+ent.frame+".png";
        heart.src = image_base + '/heart.png'
        
        var ctx = contexts[ent.layer]
        render_image(ctx,x,y,h,angle,img,s_x,s_y,base_scale*ent.scale);

        for (var i = 0;i < ent.hit_points ; ++i){
            render_image(ctx,x+16*i - ent.hit_points*8,y-24,h,angle,heart,s_x,s_y,
                        0.5)
        }
    } 


};
