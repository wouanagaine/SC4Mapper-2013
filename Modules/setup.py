from distutils.core import setup, Extension

setup(
	name = 'QFS',
	version = '1.0',
	description = 'Package for QFS compression and decompression',
	ext_modules = [
		Extension('QFS', ['qfs.c'])
	]
)

