from distutils.core import setup

setup(name='PyGenic',
		version='0.2', 
		description='Code generation library', 
		author='Cody Brocious', 
		author_email='cody.brocious@gmail.com', 
		packages=['pygenic', 'pygenic.backend'], 
		install_requires=[
			'grako',
		]
	)
