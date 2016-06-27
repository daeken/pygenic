from Backend import Backend
from C import C

@Backend.register
class Cpp(C):
	extension = 'cpp'
