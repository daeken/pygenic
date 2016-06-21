from pprint import pprint
from pygenic import *
from pygenic.backend import C, Python

module = Module()
with module.function('foo(bar : int, baz : array[int]) -> int') as func:
	func.temp = types.int(5)
	func.temp += 10
	with Switch(func.temp):
		with Case(15, 5):
			DebugPrint('%i', func.bar)
		with Case(10):
			func.temp = 100
			DebugPrint('ten!')
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
print C().generate(module)
print Python().generate(module)
