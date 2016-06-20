from contextlib import contextmanager
from Backend import Backend

def formatType(type):
	if isinstance(type, tuple):
		assert type[0] == 'array'
		return '*%s' % type[1]
	else:
		return type

class C(Backend):
	@contextmanager
	def block(self, expr):
		self.output += self.ws * self.indentation + expr + ' {\n'
		self.indentation += 1
		yield
		self.indentation -= 1
		self.output += self.ws * self.indentation + '}\n'

	def Function(self, name, ret, args, *body):
		with self.block('%s %s(%s)' % (formatType(ret), name, ', '.join('%s %s' % (formatType(type), aname) for (aname, type) in args))):
			self.passthru(*body)

	def Assign(self, name, value):
		return '%s = %s' % (self.generate(name), self.generate(value))

	def Binary(self, op, a, b):
		return '(%s) %s (%s)' % (self.generate(a), op, self.generate(b))

	def Switch(self, on, *body):
		with self.block('switch(%s)' % self.generate(on)):
			self.passthru(*body)

	def Case(self, vals, *body):
		with self.block(' '.join('case %s:' % self.generate(val) for val in vals) if len(vals) else 'default:'):
			self.passthru(*body)
			self.emit('break')

	def DebugPrint(self, fmt, *args):
		return 'printf(%s%s)' % (self.generate(fmt), (', ' + ', '.join(map(self.generate, args)) if len(args) else ''))

	def Return(self, val=None):
		if val is None:
			return 'return'
		else:
			return 'return %s' % self.generate(val)

	def Variable(self, name):
		return name

	def Value(self, val):
		if isinstance(val, int):
			return str(val)
		elif isinstance(val, str) or isinstance(val, unicode):
			val = `val + "'"`[:-2] + '"'
			assert val[0] == '"'
			return val
		else:
			print 'Unknown Value:', `val`
