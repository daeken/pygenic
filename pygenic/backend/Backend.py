from pygenic import *

class Backend(object):
	backends = {}
	@staticmethod
	def register(cls):
		Backend.backends[cls.__name__.lower()] = cls
		return cls

	ws = '\t'

	def __init__(self, hexLiterals=True):
		self.temp_i = 0

		self.hexLiterals = hexLiterals

	def tempname(self, prefix='temp'):
		self.temp_i += 1
		return '__%s_%i' % (prefix, self.temp_i)

	def generate(self, node):
		if isinstance(node, Node):
			self.output = ''
			self.indentation = 0
			self.generate(node.sexp(byName=True))
			return self.output
		elif not isinstance(node, tuple):
			return self.Value(node)

		return getattr(self, node[0])(*node[1:])

	def passthru(self, *args):
		for arg in args:
			ret = self.generate(arg)
			if ret is not None:
				self.emit(ret)
	Module = passthru
