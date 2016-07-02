from signature import signatureParser
from grako.ast import AST
from copy import deepcopy

class ParseSemantics(object):
	def _default(self, ast, *args, **kwargs):
		if isinstance(ast, AST) and 'rule' not in ast:
			ast['rule'] = ast._parseinfo.rule
		return ast

class Type(object):
	def __init__(self, name, val=None):
		self.name = name
		self.val = val

	def __call__(self, val=None):
		return Type(self.name, val)

	def __repr__(self):
		return 'pygenic.Type(%r, %r)' % (self.name, self.val)

class ObjectDict(dict):
	def __getattr__(self, name):
		return self[name]

	def __setattr__(self, name, value):
		self[name] = value

types = ObjectDict(
	char=Type('int8_t'), 
	uchar=Type('uint8_t'), 
	int8=Type('int8_t'), 
	uint8=Type('uint8_t'), 

	short=Type('int16_t'), 
	ushort=Type('uint16_t'), 
	int16=Type('int16_t'), 
	uint16=Type('uint16_t'), 

	int=Type('int32_t'), 
	int32=Type('int32_t'), 
	uint=Type('uint32_t'), 
	uint32=Type('uint32_t'), 

	int64=Type('int64_t'), 
	uint64=Type('uint64_t'), 
)

class Node(object):
	__contexts = []

	def __init__(self, *args):
		self._node_parent = None
		self._node_children = []
		for arg in args:
			self.add(arg)
		if len(Node.__contexts):
			Node.__contexts[-1].add(self)

	def __deepcopy__(self, memo):
		ret = self.__class__.__new__(self.__class__)
		ret._node_parent = None
		ret._node_children = deepcopy(self._node_children)
		return ret

	def add(self, node):
		if not isinstance(node, Node):
			self._node_children.append(node)
			return node
		if node._node_parent is not None:
			if node._node_parent is self:
				return node
			for i, elem in enumerate(node._node_parent._node_children):
				if elem is node:
					del node._node_parent._node_children[i]
					break
		self._node_children.append(node)
		node._node_parent = self
		return node

	def sexp(self, byName=False):
		return tuple(
			[self.__class__.__name__ if byName else self.__class__] + 
			[child.sexp(byName=byName) if isinstance(child, Node) else child for child in self._node_children]
		)

	def map(self, type, callback):
		def addall(ret):
			if isinstance(ret, list) or isinstance(ret, tuple):
				map(addall, ret)
			else:
				node.add(ret)
		if isinstance(self, type):
			return callback(self)
		with self.__class__() as node:
			for child in self._node_children:
				if isinstance(child, Node):
					ret = child.map(type, callback)
					if ret is not None:
						addall(ret)
				else:
					node.add(child)
		return node

	def __repr__(self):
		return `self.sexp(byName=True)`

	def __enter__(self):
		Node.__contexts.append(self)
		return self

	def __exit__(self, type, value, tb):
		Node.__contexts.pop()

	def __getattr__(self, name):
		if name.startswith('_node_'):
			return object.__getattribute__(self, name[7:])
		return self[name]
	def __getitem__(self, name):
		if isinstance(name, str) or isinstance(name, unicode):
			return self.add(Variable(name))
		else:
			return Index(self, name)

	def __setattr__(self, name, val):
		if isinstance(name, str) or isinstance(name, unicode):
			if name.startswith('_node_'):
				return object.__setattr__(self, name[7:], val)
			self[name] = val
		else:
			Assign(Index(self, name), val)
	def __setitem__(self, name, val):
		type = None
		if isinstance(val, Type):
			type, val = val.name, val.val
		if isinstance(self, Function):
			Variable(name, type).set(val)
		else:
			self.add(Variable(name, type).set(val))

	def __add__(self, right): return Binary('+', self, right)
	def __sub__(self, right): return Binary('-', self, right)
	def __mul__(self, right): return Binary('*', self, right)
	def __div__(self, right): return Binary('/', self, right)
	def __floordiv__(self, right): return Binary('//', self, right)
	def __pow__(self, right): return Binary('**', self, right)

	def __lshift__(self, right): return Binary('<<', self, right)
	def __rshift__(self, right): return Binary('>>', self, right)
	def __and__(self, right): return Binary('&', self, right)
	def __or__(self, right): return Binary('|', self, right)
	def __xor__(self, right): return Binary('^', self, right)

	def __lt__(self, right): return Binary('<', self, right)
	def __le__(self, right): return Binary('<=', self, right)
	def __eq__(self, right): return Binary('==', self, right)
	def __ne__(self, right): return Binary('!=', self, right)
	def __gt__(self, right): return Binary('>', self, right)
	def __ge__(self, right): return Binary('>=', self, right)

class Variable(Node):
	def set(self, val):
		return Assign(self, val)

	def __setitem__(self, name, val):
		Assign(Index(self, name), val)

class Assign(Node):
	pass

class Index(Node):
	pass

class Unary(Node):
	pass

class Binary(Node):
	pass

class And(Node):
	pass

class Or(Node):
	pass

class Module(Node):
	pass

class Comment(Node):
	pass

class Function(Node):
	def __init__(self, signature=None):
		if signature is not None:
			name, args, ret = self.parse(signature)
			Node.__init__(self, name, ret, args)
		else:
			Node.__init__(self)

	def parse(self, signature):
		ast = signatureParser(parseinfo=True).parse(signature, 'signature', semantics=ParseSemantics())
		name = ast['name']
		if ast['args'] is None:
			arglist = []
		else:
			arglist = [ast['args'][0]] + ast['args'][1]
		rettype = ast['returns']
		return name, tuple((arg['name'], self.parseType(arg['type'])) for arg in arglist), self.parseType(rettype)

	def parseType(self, type):
		if isinstance(type, AST):
			return (type['cls'], self.parseType(type['arg']))
		elif type in types:
			return types[type]
		else:
			return Type(type)

class Switch(Node):
	pass

class Case(Node):
	def __init__(self, *matches):
		Node.__init__(self)
		self.add(matches)

	def add(self, node):
		if isinstance(node, Node):
			return Node.add(self, node)
		if isinstance(node, Node) or not (len(self._node_children) == 1 and self._node_children[0] == ()):
			return Node.add(self, node)

		self._node_children[0] = node
		return node

class If(Node):
	pass

class Elif(Node):
	pass

class Else(Node):
	pass

class While(Node):
	pass

class DoWhile(Node):
	pass

class Call(Node):
	pass

class DebugPrint(Node):
	pass

class Return(Node):
	pass

class Cast(Node):
	pass
