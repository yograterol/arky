# -*- encoding: utf8 -*-
# © Toons

import os, sys, threading, logging, requests, random

__PY3__ = True if sys.version_info[0] >= 3 else False
if __PY3__: from io import BytesIO as StringIO
else: from StringIO import StringIO

logging.getLogger('requests').setLevel(logging.CRITICAL)

choose = lambda obj: obj[int(random.random()*len(obj))%len(obj)]
# deal with home directory
HOME = os.path.join(os.environ["HOMEDRIVE"], os.environ["HOMEPATH"]) if "win" in sys.platform else \
       os.environ.get("HOME", ".")


def setInterval(interval):
	""" threaded decorator
>>> @setInterval(10)
... def tick(): print("Tick")
>>> stop = tick() # print 'Tick' every 10 sec
>>> type(stop)
<class 'threading.Event'>
>>> stop.set() # stop printing 'Tick' every 10 sec
"""
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


def arkydify(dic):
	result = ArkyDict()
	for k,v in dic.items():
		if isinstance(v, dict): setattr(result, k, arkydify(v))
		else: setattr(result, k, v)
	return result


class ArkyDict(dict):
	"""
Python dict with javascript behaviour.
>>> ad = ArkyDict()
>>> ad["key1"] = "value1"
>>> ad.key2 = "value2"
>>> sorted(ad.items(), key=lambda e:e[0])
[('key1', 'value1'), ('key2', 'value2')]
"""
	def __setattr__(self, attr, value): return dict.__setitem__(self, attr, value)
	def __getattr__(self, attr, default=False): return dict.get(self, attr, default)
	def __delattr__(self, attr): return dict.__delitem__(self, attr)


# network parameters
NETWORKS = ArkyDict(
	testnet={
		"messagePrefix" : b"\x18Ark Testnet Signed Message:\n",
		"bip32"         : ArkyDict(public=0x043587cf, private=0x04358394),
		"pubKeyHash"    : b"\x52",
		"wif"           : b"\xef",
	}, ark={
		"messagePrefix" : b"\x18Ark Signed Message:\n",
		"bip32"         : ArkyDict(public=0x0488b21e, private=0x0488ade4),
		"pubKeyHash"    : b"\x17",
		"wif"           : b"\xaa"
	}, bitcoin={
		"messagePrefix" : b"\x18Bitcoin Signed Message:\n",
		"bip32"         : ArkyDict(public=0x0488b21e, private=0x0488ade4),
		"pubKeyHash"    : b"\x00",
		"wif"           : b"\x80"
	}, litecoin={
		"messagePrefix" : b"\x19Litecoin Signed Message:\n",
		"bip32"         : ArkyDict(public=0x019da462, private=0x019d9cfe),
		"pubKeyHash"    : b"\x30",
		"wif"           : b"\xb0"
	}
)
