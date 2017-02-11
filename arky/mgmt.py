# -*- encoding: utf8 -*-
# © Toons

from . import cfg, core, ArkyDict
import os, sys, json, queue, atexit, logging, requests, threading, binascii

# deal with home directory
if "win" in sys.platform:
	home_path = os.path.join(os.environ["HOMEDRIVE"], os.environ["HOMEPATH"])
elif "linux" in sys.platform:
	home_path = os.environ["HOME"]

logging.getLogger('requests').setLevel(logging.CRITICAL)
logging.basicConfig(
	filename  = os.path.normpath(os.path.join(home_path, "."+__name__)),
	format    = '[%(asctime)s] %(message)s',
	level     = logging.INFO,
)

LOG_LOCK = threading.Event()
MGMT_LOCK = threading.Event()
FIFO = queue.Queue()
THREADS = []


class TxLOG(threading.Thread):

	def __init__(self):
		threading.Thread.__init__(self)
		self.start()

	def run(self):
		while LOG_LOCK.isSet():
			data = cfg.__TXLOG__.get()
			if isinstance(data, ArkyDict):
				logging.log(logging.INFO, " - ".join(sorted("%s:%s" % item for item in data.items())))


class TxMGMT(threading.Thread):

	def __init__(self):
		threading.Thread.__init__(self)
		self.start()

	def run(self):
		while MGMT_LOCK.isSet():
			data = FIFO.get()
			if isinstance(data, list):
				core.sendTransaction(*data)


def push(transaction, secret, secondSignature=None):
	if isinstance(transaction, core.Transaction):
		FIFO.put([secret, transaction, secondSignature])

def start():
	global THREADS
	# first, check if there still is alive thread
	if True in [t.isAlive() for t in THREADS]: stop()
	THREADS = []
	MGMT_LOCK.set()
	for i in range(cfg.__NB_THREAD__):
		THREADS.append(TxMGMT())
	LOG_LOCK.set()
	THREADS.append(TxLOG())

def stop():
	global THREADS
	# unlock TxMGMT when FIFO queue is empty
	test = [False]*(len(THREADS)-1)
	while not FIFO.empty():
		if [t.isAlive() for t in THREADS[:-1]] == test:
			FIFO.get_nowait()
	MGMT_LOCK.clear()
	# put a stop token for each TxMGMT thread in FIFO queue
	while [t.isAlive() for t in THREADS[:-1]] != test:
		FIFO.put(False)

	# unlock TxLOG one when __TXLOG__ queue is empty
	while not cfg.__TXLOG__.empty():
		if not THREADS[-1].isAlive():
			cfg.__TXLOG__.get_nowait()
	LOG_LOCK.clear()
	# put a stop token for TxLOG thread in cfg.__TXLOG__ queue
	if THREADS[-1].isAlive():
		cfg.__TXLOG__.put(False)

# start threaded managment
start()
atexit.register(stop)
