from pprint import pprint
from pygenic import *
from pygenic.backend import Cpp, JavaScript, Python

with Module() as module:
	Comment('Module level')
	with Function('foo(bar : int, baz : array[int]) -> int') as func:
		Comment('Function level')
		func.temp = types.int(5)
		func.temp += 10

		func.temp2 = types.int
		func.temp2 = func.temp

		func.temp3 = types.int(Call('test', func.temp2 + func.baz[2]))
		func.baz[2] = 100

		with While(func.temp2 > 0):
			func.temp += 1

		func.temp2 = 10
		with DoWhile(func.temp2 > 0):
			func.temp += 2

		with Switch(func.temp):
			with Case(15, 5):
				DebugPrint('%i', func.bar)
			with Case(10):
				func.temp = 100
				DebugPrint('ten!')
				Comment('Deep')
			with Case():
				with If(And(func.temp > 50, func.temp < 100)):
					DebugPrint('...')
				with Elif(func.temp == 27):
					DebugPrint('twenty-seven')
				with Else():
					DebugPrint('weird')
				DebugPrint('other %i', func.temp)
		Return(func.temp)

pprint(module.sexp(byName=True))
print Cpp().generate(module)
print JavaScript().generate(module)
print Python().generate(module)
