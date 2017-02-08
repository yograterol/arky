# -*- encoding: utf8 -*-
# © Toons
import sys, threading

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
>>> sorted(ad.items(), key=lambda e:e[0])
[('key1', 'value1'), ('key2', 'value2')]
"""
	__setattr__ = lambda obj,*a,**k: dict.__setitem__(obj, *a, **k)
	__getattr__ = lambda obj,*a,**k: dict.__getitem__(obj, *a, **k)
	__delattr__ = lambda obj,*a,**k: dict.__delitem__(obj, *a, **k)


# threaded decorator
def setInterval(interval):
	def decorator(function):
		def wrapper(*args, **kwargs):
			stopped = threading.Event()

			def loop(): # executed in another thread
				while not stopped.wait(interval): # until stopped
					function(*args, **kwargs)

			t = threading.Thread(target=loop)
			t.daemon = True # stop if the program exits
			t.start()
			return stopped
		return wrapper
	return decorator
