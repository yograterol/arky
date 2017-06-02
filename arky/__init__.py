# -*- encoding: utf8 -*-
# © Toons
__version__ = "0.2.0"

import os, imp, sys, threading, logging, requests, random

logging.getLogger('requests').setLevel(logging.CRITICAL)
__PY3__ = True if sys.version_info[0] >= 3 else False
if __PY3__: from io import BytesIO as StringIO
else: from StringIO import StringIO

main_is_frozen = lambda: (hasattr(sys, "frozen") or hasattr(sys, "importers") or imp.is_frozen("__main__"))

# deal with home directory
ROOT = os.path.normpath(os.path.abspath(os.path.dirname(sys.executable if main_is_frozen() else __file__)))
HOME = os.path.join(os.environ["HOMEDRIVE"], os.environ["HOMEPATH"]) if "win" in sys.platform else \
       os.environ.get("HOME", ".")

logging.basicConfig(
	filename  = os.path.normpath(os.path.join(HOME, "."+__name__)),
	format    = '[%(asctime)s] %(message)s',
	level     = logging.INFO,
)

# def redirectLog(folder=None, console=False):
# 	logger = logging.getLogger()
# 	if folder:
# 		formatter = logging.Formatter('[%(asctime)s] %(message)s')
# 		file_handler = logging.FileHandler(os.path.normpath(os.path.join(folder, "tx.log")), 'a')
# 		file_handler.setLevel(logging.INFO)
# 		file_handler.setFormatter(formatter)
# 		for handler in logger.handlers[:]:
# 			logger.removeHandler(handler)
# 		logger.addHandler(file_handler)
# 	if console:
# 		console = logging.StreamHandler()
# 		console.setFormatter(logging.Formatter('%(message)s'))
# 		console.setLevel(logging.INFO)
# 		logger.addHandler(console)
# redirectLog(HOME)

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
	}, devnet={
		"messagePrefix" : b"\x18Ark Devnet Signed Message:\n",
		"bip32"         : ArkyDict(public=0x043587cf, private=0x04358394),
		"pubKeyHash"    : b"\x1e",
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
	}
)

SEEDLIST = ArkyDict(
	testnet=[
	], devnet=[
		"http://167.114.43.48:4002",
		"http://167.114.29.49:4002",
		"http://167.114.43.43:4002",
		"http://167.114.29.54:4002",
		"http://167.114.29.45:4002",
		"http://167.114.29.40:4002",
		"http://167.114.29.56:4002",
		"http://167.114.43.35:4002",
		"http://167.114.29.51:4002",
		"http://167.114.29.59:4002",
		"http://167.114.43.42:4002",
		"http://167.114.29.34:4002",
		"http://167.114.29.62:4002",
		"http://167.114.43.49:4002",
		"http://167.114.29.44:4002",
		"http://167.114.43.37:4002",
		"http://167.114.29.63:4002",
		"http://167.114.29.42:4002",
		"http://167.114.29.48:4002",
		"http://167.114.29.61:4002",
		"http://167.114.43.36:4002",
		"http://167.114.29.57:4002",
		"http://167.114.43.33:4002",
		"http://167.114.29.52:4002",
		"http://167.114.29.50:4002",
		"http://167.114.43.47:4002",
		"http://167.114.29.47:4002",
		"http://167.114.29.36:4002",
		"http://167.114.29.35:4002",
		"http://167.114.43.39:4002",
		"http://167.114.43.45:4002",
		"http://167.114.29.46:4002",
		"http://167.114.29.41:4002",
		"http://167.114.43.34:4002",
		"http://167.114.29.43:4002",
		"http://167.114.43.41:4002",
		"http://167.114.29.60:4002",
		"http://167.114.43.32:4002",
		"http://167.114.29.55:4002",
		"http://167.114.29.53:4002",
		"http://167.114.29.38:4002",
		"http://167.114.43.40:4002",
		"http://167.114.29.32:4002",
		"http://167.114.43.46:4002",
		"http://167.114.43.38:4002",
		"http://167.114.29.33:4002",
		"http://167.114.43.44:4002",
		"http://167.114.43.50:4002",
		"http://167.114.29.37:4002",
		"http://167.114.29.58:4002",
		"http://167.114.29.39:4002",
	], mainnet=[
		"http://5.39.9.240:4001",
		"http://5.39.9.241:4001",
		"http://5.39.9.242:4001",
		"http://5.39.9.243:4001",
		"http://5.39.9.244:4001",
		"http://5.39.9.250:4001",
		"http://5.39.9.251:4001",
		"http://5.39.9.252:4001",
		"http://5.39.9.253:4001",
		"http://5.39.9.254:4001",
		"http://5.39.9.255:4001",
		"http://5.39.53.48:4001",
		"http://5.39.53.49:4001",
		"http://5.39.53.50:4001",
		"http://5.39.53.51:4001",
		"http://5.39.53.52:4001",
		"http://5.39.53.53:4001",
		"http://5.39.53.54:4001",
		"http://5.39.53.55:4001",
		"http://37.59.129.160:4001",
		"http://37.59.129.161:4001",
		"http://37.59.129.162:4001",
		"http://37.59.129.163:4001",
		"http://37.59.129.164:4001",
		"http://37.59.129.165:4001",
		"http://37.59.129.166:4001",
		"http://37.59.129.167:4001",
		"http://37.59.129.168:4001",
		"http://37.59.129.169:4001",
		"http://37.59.129.170:4001",
		"http://37.59.129.171:4001",
		"http://37.59.129.172:4001",
		"http://37.59.129.173:4001",
		"http://37.59.129.174:4001",
		"http://37.59.129.175:4001",
		"http://193.70.72.80:4001",
		"http://193.70.72.81:4001",
		"http://193.70.72.82:4001",
		"http://193.70.72.83:4001",
		"http://193.70.72.84:4001",
		"http://193.70.72.85:4001",
		"http://193.70.72.86:4001",
		"http://193.70.72.87:4001",
		"http://193.70.72.88:4001",
		"http://193.70.72.89:4001",
		"http://193.70.72.90:4001",
		"http://167.114.29.37:4001",
		"http://167.114.29.38:4001",
		"http://167.114.29.39:4001",
		"http://167.114.29.40:4001",
		"http://167.114.29.41:4001",
		"http://167.114.29.42:4001",
		"http://167.114.29.43:4001",
		"http://167.114.29.44:4001",
		"http://167.114.29.45:4001",
		"http://167.114.29.46:4001",
		"http://167.114.29.47:4001",
		"http://167.114.29.48:4001",
		"http://167.114.29.49:4001",
		"http://167.114.29.50:4001",
		"http://167.114.29.51:4001",
		"http://167.114.29.52:4001",
		"http://167.114.29.53:4001",
		"http://167.114.29.54:4001",
		"http://167.114.29.55:4001",
		"http://167.114.29.56:4001",
		"http://167.114.29.57:4001",
		"http://167.114.29.58:4001",
		"http://167.114.29.59:4001",
		"http://167.114.29.60:4001",
		"http://167.114.29.61:4001",
		"http://167.114.29.62:4001",
		"http://167.114.29.63:4001",
		"http://167.114.43.32:4001",
		"http://167.114.43.33:4001",
		"http://167.114.43.34:4001",
		"http://167.114.43.35:4001",
		"http://167.114.43.36:4001",
		"http://167.114.43.37:4001",
		"http://167.114.43.38:4001",
		"http://167.114.43.39:4001",
		"http://167.114.43.40:4001",
		"http://167.114.43.41:4001",
		"http://167.114.43.42:4001",
		"http://167.114.43.43:4001",
		"http://167.114.43.44:4001",
		"http://167.114.43.45:4001",
		"http://167.114.43.46:4001",
		"http://167.114.43.47:4001",
		"http://167.114.43.48:4001",
		"http://167.114.43.49:4001",
		"http://167.114.43.50:4001",
		"http://5.135.102.88:4001",
		"http://5.135.102.89:4001",
		"http://5.135.102.90:4001",
		"http://5.135.102.91:4001",
		"http://5.135.102.92:4001",
		"http://5.135.102.93:4001",
		"http://5.135.102.94:4001",
		"http://5.135.102.95:4001",
		"http://137.74.79.168:4001",
		"http://137.74.79.169:4001",
		"http://137.74.79.170:4001",
		"http://137.74.79.171:4001",
		"http://137.74.79.172:4001",
		"http://137.74.79.173:4001",
		"http://137.74.79.174:4001",
		"http://137.74.79.175:4001",
		"http://137.74.79.184:4001",
		"http://137.74.79.185:4001",
		"http://137.74.79.186:4001",
		"http://137.74.79.187:4001",
		"http://137.74.79.188:4001",
		"http://137.74.79.189:4001",
		"http://137.74.79.190:4001",
		"http://137.74.79.191:4001",
		"http://137.74.90.192:4001",
		"http://137.74.90.193:4001",
		"http://137.74.90.194:4001",
		"http://137.74.90.195:4001",
		"http://137.74.90.196:4001",
		"http://137.74.90.197:4001",
		"http://137.74.11.160:4001",
		"http://137.74.11.161:4001",
		"http://137.74.11.162:4001",
		"http://137.74.11.163:4001",
		"http://137.74.11.164:4001",
		"http://137.74.11.165:4001",
		"http://137.74.11.166:4001",
		"http://137.74.11.167:4001",
		"http://188.165.158.66:4001",
		"http://188.165.158.67:4001",
		"http://213.32.41.104:4001",
		"http://213.32.41.105:4001",
		"http://213.32.41.106:4001",
		"http://213.32.41.107:4001",
		"http://213.32.41.108:4001",
		"http://213.32.41.109:4001",
		"http://213.32.41.110:4001",
		"http://213.32.41.111:4001",
		"http://51.255.105.54:4001",
		"http://51.255.105.55:4001",
		"http://46.105.160.106:4001",
	]
)
