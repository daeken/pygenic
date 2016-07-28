from contextlib import contextmanager
from Backend import Backend

@Backend.register
class JavaScript(Backend):
	extension = 'js'

	@contextmanager
	def block(self, expr, end=None, indent=True):
		self.output += self.ws * self.indentation + expr + ' {\n'
		if indent:
			self.indentation += 1
		yield
		if indent:
			self.indentation -= 1
		if end is None:
			self.output += self.ws * self.indentation + '}\n'
		else:
			self.output += self.ws * self.indentation + '} %s;\n' % end

	def emit(self, stmt):
		self.output += self.ws * self.indentation + stmt + ';\n'

	def Comment(self, comment):
		self.output += self.ws * self.indentation + '/* %s */\n' % comment

	def Function(self, name, ret, args, *body):
		with self.block('function %s(%s)' % (name, ', '.join(aname for (aname, type) in args))):
			self.passthru(*body)

	def Assign(self, name, value):
		return '%s = %s' % (self.generate(name), self.generate(value))

	def Unary(self, op, a):
		return '%s(%s)' % (op, self.generate(a))

	def Binary(self, op, a, b):
		return '(%s) %s (%s)' % (self.generate(a), op, self.generate(b))

	def And(self, *args):
		if len(args) == 0:
			return 'true'
		elif len(args) == 1:
			return args[0]
		else:
			return ' && '.join('(%s)' % self.generate(arg) for arg in args)

	def Or(self, *args):
		if len(args) == 0:
			return 'true'
		elif len(args) == 1:
			return args[0]
		else:
			return ' || '.join('(%s)' % self.generate(arg) for arg in args)

	def Switch(self, on, *body):
		with self.block('switch(%s)' % self.generate(on), indent=False):
			self.passthru(*body)

	def Case(self, vals, *body):
		with self.block(' '.join('case %s:' % self.generate(val) for val in vals) if len(vals) else 'default:'):
			self.passthru(*body)
			self.emit('break')

	def If(self, expr, *body):
		with self.block('if(%s)' % self.generate(expr)):
			self.passthru(*body)

	def Elif(self, expr, *body):
		with self.block('else if(%s)' % self.generate(expr)):
			self.passthru(*body)

	def Else(self, *body):
		with self.block('else'):
			self.passthru(*body)

	def While(self, expr, *body):
		with self.block('while(%s)' % self.generate(expr)):
			self.passthru(*body)

	def DoWhile(self, expr, *body):
		with self.block('do', end='while(%s)' % self.generate(expr)):
			self.passthru(*body)

	def DebugPrint(self, fmt, *args):
		return 'console.log(%s%s)' % (self.generate(fmt), (', ' + ', '.join(map(self.generate, args)) if len(args) else ''))

	def Call(self, func, *args):
		return '%s(%s)' % (func, ', '.join(map(self.generate, args)))

	def Return(self, val=None):
		if val is None:
			return 'return'
		else:
			return 'return %s' % self.generate(val)

	def Variable(self, name, type=None):
		if type is None:
			return name
		else:
			return 'var %s' % name

	def Index(self, base, index):
		return '(%s)[%s]' % (self.generate(base), self.generate(index))

	def Value(self, val):
		if val is False or val is True:
			return 'false' if val is False else 'true'
		elif isinstance(val, int):
			if self.hexLiterals:
				if val >= 0:
					return '0x%x' % val
				else:
					return '-0x%x' % -val
			else:
				return str(val)
		elif isinstance(val, str):
			return `val`
		elif isinstance(val, unicode):
			return `val`[1:] # Cut off `u` prefix
		elif val is None:
			return '0'
		else:
			print 'Unknown Value:', `val`

	def Cast(self, value, type):
		return value # XXX: Handle necessary casting
