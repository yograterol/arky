# -*- encoding: utf8 -*-
# © Toons

from . import cfg, core, ArkyDict
import json, queue, atexit, logging, threading

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='[%(asctime)s %(threadName)s] %(message)s')

__FIFO__ = queue.Queue()
__RESULT__ = queue.Queue()

class TxLog(threading.Thread):
	alive = False

	def __init__(self):
		TxLog.alive = True
		threading.Thread.__init__(self)
		self.setDaemon(True)
		self.start()

	@staticmethod
	def stop():
		TxLog.alive = False

	def run(self):
		while TxMGMT.alive or not __RESULT__.empty():
			data = __RESULT__.get()
			if data: logger.info(data)
			else: break


class TxMGMT(threading.Thread):
	alive = False
	attempt = 10

	def __init__(self):
		TxMGMT.alive = True
		threading.Thread.__init__(self)
		self.setDaemon(True)
		self.start()

	@staticmethod
	def stop():
		TxMGMT.alive = False

	def run(self):
		while TxMGMT.alive or not __FIFO__.empty():
			data = __FIFO__.get()
			if data:
				transaction, secret, secondSignature = data
				success, attempt = False, TxMGMT.attempt
				while not success or attempt > 0:
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
				result.transaction = "%r" % transaction
				__RESULT__.put(result)
			else:
				break


def push(transaction, secret, secondSignature=None):
	if isinstance(transaction, core.Transaction):
		__FIFO__.put([transaction, secret, secondSignature])

def start():
	threads = []
	for i in range(cfg.__NB_THREAD__):
		threads.append(TxMGMT())
	threads.append(TxLog())
	return threads

def stop():
	TxLog.stop()
	__RESULT__.put(False)
	TxMGMT.stop()
	for i in range(cfg.__NB_THREAD__):
		__FIFO__.put(False)

atexit.register(stop)
