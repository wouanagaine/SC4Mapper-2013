from distutils.core import setup, Extension

setup(
	name = 'QFS',
	version = '1.0',
	description = 'Package for QFS compression and decompression',
	ext_modules = [
		Extension('QFS', ['qfs.c'])
	]
)

setup(
	name = 'tools3D',
	version = '1.0',
	description = 'tools and utilities for 3D things',
	ext_modules = [
		Extension('tools3D', ['tools3D.cpp'])
	]
)

