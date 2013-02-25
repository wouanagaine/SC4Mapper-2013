#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

def encodeFilename(s):
	"""
	@param s The name of the file (of type unicode)
	"""

	if type(s) == type( '' ):
		return s
	assert type(s) == type(u'')

	return s.encode(sys.getfilesystemencoding(), 'ignore')
