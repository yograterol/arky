# -*- encoding: utf8 -*-
# © Toons
import sys

__PY3__ = True if sys.version_info[0] >= 3 else False
if __PY3__:
	from io import BytesIO as StringIO
	long = int
else:
	from StringIO import StringIO

class ArkyDict(dict):
	"""
Python dict with javascript behaviour.
>>> ad = ArkyDict()
>>> ad["key1"] = "value1"
>>> ad.key2 = "value2"
>>> ad
{'key2': 'value2', 'key1': 'value1'}
"""
	__setattr__ = lambda obj,*a,**k: dict.__setitem__(obj, *a, **k)
	__getattr__ = lambda obj,*a,**k: dict.__getitem__(obj, *a, **k)
	__delattr__ = lambda obj,*a,**k: dict.__delitem__(obj, *a, **k)
