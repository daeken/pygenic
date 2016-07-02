from contextlib import contextmanager
from Backend import Backend

@Backend.register
class Python(Backend):
	extension = 'py'
	
	@contextmanager
	def block(self, expr):
		self.output += self.ws * self.indentation + expr + ':\n'
		self.indentation += 1
		yield
		self.indentation -= 1

	def emit(self, stmt):
		self.output += self.ws * self.indentation + stmt + '\n'

	def Comment(self, comment):
		self.output += self.ws * self.indentation + 'pass # %s\n' % comment

	def Function(self, name, ret, args, *body):
		with self.block('def %s(%s)' % (name, ', '.join(aname for (aname, type) in args))):
			self.passthru(*body)

	def Assign(self, name, value):
		return '%s = %s' % (self.generate(name), self.generate(value))

	def Unary(self, op, a):
		return '%s(%s)' % (op, self.generate(a))
	
	def Binary(self, op, a, b):
		return '(%s) %s (%s)' % (self.generate(a), op, self.generate(b))

	def And(self, *args):
		if len(args) == 0:
			return 'True'
		elif len(args) == 1:
			return args[0]
		else:
			return ' and '.join('(%s)' % self.generate(arg) for arg in args)

	def Or(self, *args):
		if len(args) == 0:
			return 'True'
		elif len(args) == 1:
			return args[0]
		else:
			return ' or '.join('(%s)' % self.generate(arg) for arg in args)

	def Switch(self, on, *body):
		temp = self.tempname('switch')
		self.emit('%s = %s' % (temp, self.generate(on)))
		cases, default = [], None
		for elem in body:
			assert elem[0] == 'Case'
			if len(elem[1]):
				cases.append(elem)
			else:
				default = elem
		for i, elem in enumerate(cases):
			with self.block('%s %s' % ('if' if i == 0 else 'elif', ' or '.join('%s == %s' % (temp, x) for x in elem[1]))):
				self.passthru(*elem[2:])
		if default is not None:
			if len(cases) == 0:
				self.passthru(*default[2:])
			else:
				with self.block('else'):
					self.passthru(*default[2:])

	def If(self, expr, *body):
		with self.block('if %s' % self.generate(expr)):
			self.passthru(*body)

	def Elif(self, expr, *body):
		with self.block('elif %s' % self.generate(expr)):
			self.passthru(*body)

	def Else(self, *body):
		with self.block('else'):
			self.passthru(*body)

	def While(self, expr, *body):
		with self.block('while %s' % self.generate(expr)):
			self.passthru(*body)

	def DoWhile(self, expr, *body):
		with self.block('while True'):
			self.passthru(*body)
			with self.block('if not (%s)' % self.generate(expr)):
				self.emit('break')

	def DebugPrint(self, fmt, *args):
		return 'print %s%s' % (self.generate(fmt), (' %% (%s)' % ', '.join(map(self.generate, args)) if len(args) else ''))

	def Call(self, func, *args):
		return '%s(%s)' % (func, ', '.join(map(self.generate, args)))

	def Return(self, val=None):
		if val is None:
			return 'return'
		else:
			return 'return %s' % self.generate(val)

	def Variable(self, name, type=None):
		return name

	def Index(self, base, index):
		return '(%s)[%s]' % (self.generate(base), self.generate(index))

	def Value(self, val):
		if self.hexLiterals and isinstance(val, int) and not isinstance(val, bool):
			if val >= 0:
				return '0x%x' % val
			else:
				return '-0x%x' % -val
		else:
			return `val`

	def Cast(self, value, type):
		# XXX: This needs to handle signedness and int/float conversions!
		return '(%s)' % self.generate(value)
