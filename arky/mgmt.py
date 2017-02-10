# -*- encoding: utf8 -*-
# © Toons

from . import cfg, core, ArkyDict
import os, json, queue, atexit, logging, requests, threading, binascii

logging.getLogger('requests').setLevel(logging.CRITICAL)
logging.basicConfig(
	filename  = os.path.normpath(os.path.join(os.path.dirname(__file__), __name__ + ".log")),
	format    = '[%(asctime)s] %(message)s',
	level     = logging.INFO,
)

__LOG_LOCK__ = threading.Event()
__MGMT_LOCK__ = threading.Event()
__FIFO__ = queue.Queue()


class TxLOG(threading.Thread):

	def __init__(self):
		threading.Thread.__init__(self)
		self.start()

	def run(self):
		while __LOG_LOCK__.isSet():
			data = cfg.__TXLOG__.get()
			if data:
				logging.log(logging.INFO, " - ".join(sorted("%s:%s" % item for item in data.items())))


class TxMGMT(threading.Thread):
	attempt = 10

	def __init__(self):
		threading.Thread.__init__(self)
		self.start()

	def run(self):
		while __MGMT_LOCK__.isSet():
			data = __FIFO__.get()
			if data:
				transaction, secret, secondSignature = data
				success, attempt = False, TxMGMT.attempt
				while not success and attempt > 0:
					attempt -= 1
					# 1s shift timestamp for hash change
					transaction.timestamp += 1
					transaction.sign(secret)
					if secondSignature:
						transaction.seconSign(secondSignature)

					result = ArkyDict(json.loads(requests.post(
						cfg.__URL_BASE__+"/peer/transactions",
						data=json.dumps({"transactions": [transaction.serialize()]}),
						headers=cfg.__HEADERS__
					).text))

					success = result["success"]

				result.attempt = TxMGMT.attempt - attempt
				if not success:
					result.signature = binascii.hexlify(transaction.signature)
					delattr(transaction, "signature")
					result.getbyte = binascii.hexlify(core.getBytes(transaction))
				else:
					result.transaction = "%r" % transaction
				cfg.__TXLOG__.put(result)


def push(transaction, secret, secondSignature=None):
	if isinstance(transaction, core.Transaction):
		print(">>> put:", [transaction, secret, secondSignature])
		__FIFO__.put([transaction, secret, secondSignature])

def start():
	global threads
	threads = []
	__MGMT_LOCK__.set()
	for i in range(cfg.__NB_THREAD__):
		threads.append(TxMGMT())
	__LOG_LOCK__.set()
	threads.append(TxLOG())

def stop():
	# unlock TxMGMT when __FIFO__ queue is empty
	test = [False]*cfg.__NB_THREAD__
	while not __FIFO__.empty():
		if [t.isAlive() for t in threads[:cfg.__NB_THREAD__]] == test:
			__FIFO__.get_nowait()
	__MGMT_LOCK__.clear()
	# put a stop token for each TxMGMT thread in __FIFO__ queue
	while [t.isAlive() for t in threads[:cfg.__NB_THREAD__]] != test:
		__FIFO__.put(False)

	# unlock TxLOG one when __TXLOG__ queue is empty
	while not cfg.__TXLOG__.empty():
		if not threads[-1].isAlive():
			cfg.__TXLOG__.get_nowait()
	__LOG_LOCK__.clear()
	# put a stop token for TxLOG thread in cfg.__TXLOG__ queue
	if threads[-1].isAlive():
		cfg.__TXLOG__.put(False)

# start threaded managment
start()
