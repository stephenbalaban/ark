function lerp_frame(first,last){
    return first + (last-first)*(anim_index);
}

var animations = {

    'base' : function(contexts, ent) {

        if (ent.olds && ent.olds['pos']) {
            var x = lerp_frame(ent.olds.pos[0], ent.pos[0]);
            var y = lerp_frame(ent.olds.pos[1], ent.pos[1]);
        } else {
            var x = ent.pos[0];
            var y = ent.pos[1];
        }


        x = entity_size*(x+0.5)
        y = entity_size*(y + 0.5)
    
        var s_x = ent.size[0]; 
        var s_y = ent.size[1];
        var angle = ent.angle;
        var img = new Image();
	img.src = image_base + ent.tex;

	var ctx = contexts[ent.layer]
        ctx.translate(x,y);
        ctx.rotate(angle);               
        ctx.drawImage(img, -s_x, -s_y)
        ctx.rotate(-angle);
        ctx.translate(-x,-y);
    },

    'dude' : function(contexts, ent) {

	
	
        if (ent.olds && ent.olds['pos']) {
	    //log_message("lerping at"+anim_index+"from"+ent.olds.pos[0]+
            //			"to"+ent.pos[0]);
	    var x = lerp_frame(ent.olds.pos[0], ent.pos[0]);
            var y = lerp_frame(ent.olds.pos[1], ent.pos[1]);
        } else {
            var x = ent.pos[0];
            var y = ent.pos[1];
        }


        x = entity_size*(x+0.5)
        y = entity_size*(y + 0.5)
    
        var s_x = ent.size[0]; 
        var s_y = ent.size[1];
        var angle = ent.angle;
        var img = new Image();

	if (! ent.frame)
	    ent.frame = 0;

	if (ent.olds.walking && anim_index < 1 )
	    ent.frame =  (ent.frame+1) % 3;
	img.src = image_base + ent.tex+"_"+ent.frame+".png";

	var ctx = contexts[ent.layer]
        ctx.translate(x,y);
        ctx.rotate(angle);               
        ctx.drawImage(img, -s_x, -s_y)
        ctx.rotate(-angle);
        ctx.translate(-x,-y);
    } 


};
