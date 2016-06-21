from signature import signatureParser
from grako.ast import AST

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
	uint=Type('uint32_t'), 
)

class Node(object):
	__contexts = []

	def __init__(self, *args):
		self.__parent = None
		self.__children = []
		for arg in args:
			self.add(arg)
		if len(Node.__contexts):
			Node.__contexts[-1].add(self)

	def add(self, node):
		if not isinstance(node, Node):
			self.__children.append(node)
			return node
		if node.__parent is not None:
			if node.__parent is self:
				return node
			node.__parent.__children.remove(node)
		self.__children.append(node)
		node.__parent = self
		return node

	def sexp(self, byName=False):
		return tuple([self.__class__.__name__ if byName else self.__class__] + [child.sexp(byName=byName) if isinstance(child, Node) else child for child in self.__children])

	def __repr__(self):
		print 'foo'
		return `self.sexp(byName=True)`

	def __enter__(self):
		Node.__contexts.append(self)
		return self

	def __exit__(self, type, value, tb):
		Node.__contexts.pop()

	def __getattr__(self, name):
		if name.startswith('_Node__'):
			return object.__getattribute__(self, name[7:])
		return self[name]
	def __getitem__(self, name):
		return self.add(Variable(name))

	def __setattr__(self, name, val):
		if name.startswith('_Node__'):
			return object.__setattr__(self, name[7:], val)
		self[name] = val
	def __setitem__(self, name, val):
		type = None
		if isinstance(val, Type):
			type, val = val.name, val.val
		if isinstance(self, Function):
			Variable(name, type).set(val)
		else:
			self.add(Variable(name, type).set(val))

class Variable(Node):
	def set(self, val):
		return Assign(self, val)

	def __add__(self, right):
		return Binary('+', self, right)

	def __sub__(self, right):
		return Binary('-', self, right)

class Assign(Node):
	pass

class Binary(Node):
	pass

class Module(Node):
	def function(self, signature):
		func = Function(signature=signature)
		self.add(func)
		return func

class Function(Node):
	def __init__(self, signature=None):
		name, args, ret = self.parse(signature)
		Node.__init__(self, name, ret, args)

	def parse(self, signature):
		ast = signatureParser(parseinfo=True).parse(signature, 'signature', semantics=ParseSemantics())
		name = ast['name']
		if ast['args'] is None:
			arglist = []
		else:
			arglist = [ast['args'][0]] + ast['args'][1]
		rettype = ast['returns']
		return name, tuple((arg['name'], self.parseType(arg['type'])) for arg in arglist), rettype

	def parseType(self, type):
		if isinstance(type, AST):
			return (type['cls'], self.parseType(type['arg']))
		else:
			return type

class Switch(Node):
	pass

class Case(Node):
	def __init__(self, *matches):
		Node.__init__(self)
		self.add(matches)

class DebugPrint(Node):
	pass

class Return(Node):
	pass
