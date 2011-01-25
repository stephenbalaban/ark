# vector2.py
#   this class contains vector objects
# usefull for storing and minipulating 2space vectors

import math
sin = math.sin
cos = math.cos
acos = math.acos
sqrt = math.sqrt

class vector2:
	"""This class stores a 2d vector.
	All vector operations are overloaded."""


	def __init__(self, xpart, ypart):
		"""Sets up a vector with x lengths and y lengths """
		self.x = xpart
		self.y = ypart


	#reload the __str__ vector so that they can be overloaded
	def  __str__(self):
		"""Return the vector in string form."""
		return "Vector2("+str(self.x)+", "+str(self.y)+")"


	#over load the add, subtract operators so you can do vector math
	def __add__(self, other):
		return vector2(self.x + other.x, self.y + other.y)

	def __sub__(self, other):
		return vector2(self.x - other.x, self.y - other.y)

	def __neg__(self):
		return vector2(-self.x, -self.y)

	def __mul__(self, other):
	#check to see if they're trying to do a dot product
		if(other.__class__ == self.__class__):
		  return self.dot_product(other)
		else:
		  return vector2(self.x*other, self.y*other)
	  
	def __div__(self, other):
	# just multiply by the inberse of the scalar
		return self*(1.0/other)


	def dot_product(self, other):
		return self.x*other.x  + self.y*other.y

	#what is the length squared of the vector?
	#usefull because it's easy to compute

	def length_squared(self):
		"""Returns the length of the vector, squared.
		Easy to compute. Use this when exact length isn't needed."""
		return self.x*self.x + self.y*self.y

	def length(self):
		"""Returns the length of the vector."""
		return sqrt(self.length_squared())


	def angle(self):
		"""Returns the angle this vector makes with the vertical."""
		#the dot product of a and b is abcos(theta)
		#normalize this vector, dot it with (0,-1) and take the acos of the result
		angle = acos( self.normalize()*vector2(1,0))

		#the only issue is that this will always return a positive angle
		#so if  y is  negative,make the angle negative
		if(self.y < 0):
		  angle = math.pi*2 - angle
		return angle

	def normalize(self):
		"""returns a noramlized (unit length) version of this vector"""
		return self*(1/self.length())

	def scale(self,scalar):
		return vector2(self.x*scalar, self.y*scalar)


	def copy(self):
		return vector2(self.x, self.y)


	def is_zero(self):
		return self.x == 0 and self.y == 0

	def __repr__(self):
		return str(self)

	def to_json(self):
		return (self.x, self.y)

ZERO_VECTOR = vector2(0,0)
def get_unit_vector(angle):
    """
    #return a unit vector based upon the angle given
    #units with angle 0 face straight updwards
    # in the pygame coordinate system,  x and y increase downwards. 
    #increasing angle turns you counterclockwise.
    """
    angle = angle*math.pi/180
    return vector2(sin(angle), cos(angle))
		
