from PIL import Image
import sys

def chop(filename, width, height):

    im = Image.open(filename)
    sx,sy = im.size
    for x in range(sx/width):
	for y in range(sy/height):
	    coords =  (x*width,
		    y*height, 
		    (x+1)*width,
		    (y+1)*height)
	    cropped = im.crop(coords)
	    cropped.save('%s cropped %d %d %d_%d.png' % (filename, width, height ,x,y))



if __name__ == "__main__":
    if not len(sys.argv) > 3:
	print "usage: image_chop.py image width height"
    else:
	chop(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]))
	
