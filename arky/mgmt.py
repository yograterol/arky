# -*- encoding: utf8 -*-
# © Toons

from . import cfg, core, ArkyDict, HOME
import os, sys, json, atexit, logging, requests, threading, binascii, traceback

logging.basicConfig(
	filename  = os.path.normpath(os.path.join(HOME, "."+__name__)),
	format    = '[%(asctime)s] %(message)s',
	level     = logging.INFO,
)

def log_console():
	console = logging.StreamHandler()
	console.setFormatter(logging.Formatter('%(message)s'))
	console.setLevel(logging.INFO)
	logging.getLogger('').addHandler(console)

LOG_LOCK = threading.Event()
MGMT_LOCK = threading.Event()
FIFO = cfg.queue.Queue()
THREADS = []


class TxLOG(threading.Thread):

	def __init__(self):
		threading.Thread.__init__(self)
		self.start()

	def run(self):
		while LOG_LOCK.isSet():
			data = cfg.__LOG__.get()
			if isinstance(data, (ArkyDict, dict)):
				logging.log(logging.INFO, " - ".join(sorted("%s:%s" % item for item in data.items())))


class TxMGMT(threading.Thread):

	def __init__(self):
		threading.Thread.__init__(self)
		self.start()

	def run(self):
		while MGMT_LOCK.isSet():
			data = FIFO.get()
			if isinstance(data, list):
				try:
					core.sendTransaction(*data)
				except Exception as error:
					if hasattr(error, "__traceback__"):
						cfg.__LOG__.put({
							"API error": error, 
							"details": "\n"+("".join(traceback.format_tb(error.__traceback__)).rstrip())
						})
					else:
						cfg.__LOG__.put({"API error": error})


def push(transaction, secret=None, secondSecret=None):
	if isinstance(transaction, core.Transaction):
		FIFO.put([transaction, secret, secondSecret])

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

	# unlock TxLOG one when __LOG__ queue is empty
	while not cfg.__LOG__.empty():
		if not THREADS[-1].isAlive():
			cfg.__LOG__.get_nowait()
	LOG_LOCK.clear()
	# put a stop token for TxLOG thread in cfg.__LOG__ queue
	if THREADS[-1].isAlive():
		cfg.__LOG__.put(False)

# start threaded managment
start()
atexit.register(stop)
