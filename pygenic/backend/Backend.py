from pygenic import *

class Backend(object):
	ws = '\t'

	def generate(self, node):
		if isinstance(node, Node):
			self.output = ''
			self.indentation = 0
			self.generate(node.sexp(byName=True))
			return self.output
		elif not isinstance(node, tuple):
			return self.Value(node)

		return getattr(self, node[0])(*node[1:])

	def emit(self, stmt):
		self.output += self.ws * self.indentation + stmt + ';\n'

	def passthru(self, *args):
		for arg in args:
			ret = self.generate(arg)
			if ret is not None:
				self.emit(ret)
	Module = passthru
