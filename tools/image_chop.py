from PIL import Image
import sys

def chop(filename, square_size):

    im = Image.open(filename)
    for x in range(square_size):
	for y in range(square_size):
	    coords =  (x*square_size,
		    y*square_size, 
		    (x+1)*square_size,
		    (y+1)*square_size)
	    cropped = im.crop(coords)
	    cropped.save('%s cropped %d %d_%d.png' % (filename, square_size,x,y))



if __name__ == "__main__":
    chop(sys.argv[1], int(sys.argv[2]))
	
