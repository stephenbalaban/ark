from PIL import Image


def combine_images(bottom, top):
    im1 = Image.open(bottom)
    im2 = Image.open(top)

    im2 = im2.convert('RGBA')
    im1 = im1.convert('RGBA')
    im1.paste(im2, (0,0), im2)
    im1.save(top)


for a in ['grass','water']:
    for b in ['grass','water']:
	for c in ['grass', 'water']:
	    for d in ['grass','water']:
		combine_images('static/images/grass/grass/grass/grass/grass.png', 
	       'static/images/water/%s/%s/%s/%s.png' % (a,b,c,d))
     
