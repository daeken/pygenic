from pygenic import *

class Transform(object):
	def transform(self, node):
		if isinstance(node, Node):
			return self.transform(node.sexp(byName=True))
		assert isinstance(node, tuple)

		if hasattr(self, node[0]):
			return getattr(self, node[0])(*node[1:])
		else:
			print 'Unknown node to %s: %r' % (self.__class__.__name__, node)

	def passthru(self, *args):
		for arg in args:
			self.transform(arg)
	Module = passthru
