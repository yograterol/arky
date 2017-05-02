# -*- encoding: utf8 -*-
# © Toons

# only GET method is implemented, no POST or PUT for security reasons
from .. import cfg, core, ArkyDict, choose, setInterval, NETWORKS, SEEDLIST, __version__
import os, sys, json, requests, traceback, datetime, pytz
UTC = pytz.UTC

class NetworkError(Exception): pass

def log_exception(error):
	if hasattr(error, "__traceback__"):
		cfg.__LOG__.put({
			"API error": error,
			"details": "\n"+("".join(traceback.format_tb(error.__traceback__)).rstrip())
		})
	else:
		cfg.__LOG__.put({"API error": error})

# GET generic method for ARK API
def get(api, dic={}, **kw):
	"""
"""
	args = dict(dic, **kw)
	returnkey = args.pop("returnKey", False)
	try:
		text = requests.get(cfg.__URL_BASE__+api, params=args, headers=cfg.__HEADERS__, timeout=2).text
		data = json.loads(text)
	except Exception as error:
		log_exception(error)
	else:
		if data["success"]:
			return ArkyDict(data[returnkey]) if returnkey else ArkyDict(data)
	return ArkyDict()

# The only POST here that send transactions
def post_tx(url_base, *transactions):
	"""
"""
	transactions = json.dumps({"transactions": [tx.serialize() for tx in transactions]})
	try:
		text = requests.post(url_base + "/peer/transactions", data=transactions, headers=cfg.__HEADERS__, timeout=2).text
		data = json.loads(text)
	except Exception as error:
		log_exception(error)
	else:
		if data["success"]:
			return ArkyDict(data)
	return ArkyDict()

def broadcast(*transactions, secret=None, secondSecret=None):
	"""
"""
	transactions = [tx.sign(secret, secondSecret) for tx in transactions if isinstance(tx, core.Transaction)]
	if len(transactions):
		for peer in PEERS:
			post_tx(peer, *transactions)

class Loader:

	@staticmethod
	def getLoadingStatus():
		return get('/api/loader/status')

	@staticmethod
	def getSynchronisationStatus():
		return get('/api/loader/status/sync')


class Block:

	@staticmethod
	def getBlock(blockId):
		return get('/api/blocks/get', id=blockId)

	@staticmethod
	def getNethash():
		return get('/api/blocks/getNethash')

	@staticmethod
	def getBlocks():
		return get('/api/blocks')

	@staticmethod
	def getBlockchainFee():
		return get('/api/blocks/getFee')

	@staticmethod
	def getBlockchainHeight():
		return get('/api/blocks/getHeight')

	@staticmethod
	def getForgedByAccount(publicKey):
		return get('/api/delegates/forging/getForgedByAccount', generatorPublicKey=publicKey)


class Account:

	@staticmethod
	def getBalance(address):
		return get('/api/accounts/getBalance', address=address)

	@staticmethod
	def getPublicKey(address):
		return get('/api/accounts/getPublicKey', address=address)

	@staticmethod
	def getAccount(address):
		return get('/api/accounts', address=address)

	@staticmethod
	def getVotes(address):
		return get('/api/accounts/delegates', address=address)


class Delegate:

	@staticmethod
	def getDelegates(**param):
		return get('/api/delegates', **param)

	@staticmethod
	def getDelegate(username):
		return get('/api/delegates/get', username=username)

	@staticmethod
	def getVoters(publicKey):
		return get('/api/delegates/voters', publicKey=publicKey)

	@staticmethod
	def getCandidates():
		delegates = []
		while 1:
			found = Delegate.getDelegates(offset=len(delegates), limit=51).get("delegates", [])
			delegates += found
			if len(found) < 51:
				break
		return delegates


class Transaction(object):

	@staticmethod
	def getTransactionsList(**param):
		return get('/api/transactions', **param)

	@staticmethod
	def getTransaction(transactionId):
		return get('/api/transactions/get', id=transactionId)

	@staticmethod
	def getUnconfirmedTransaction(transactionId):
		return get('/api/transactions/unconfirmed/get', id=transactionId)

	@staticmethod
	def getUnconfirmedTransactions():
		return get('/api/transactions/unconfirmed')


class Peer:

	@staticmethod
	def getPeersList():
		return get('/api/peers')

	@staticmethod
	def getPeer(ip, port):
		return get('/api/peers', ip=ip, port=port)

	@staticmethod
	def getPeerVersion():
		return get('/api/peers/version')


class Multisignature:

	@staticmethod
	def getPendingMultiSignatureTransactions(publicKey):
		return get('/api/multisignatures/pending', publicKey=publicKey)

	@staticmethod
	def getAccountsOfMultisignature(publicKey):
		return post('/api/multisignatures/accounts', publicKey=publicKey)


def use(network="testnet", broadcast=5):
	"""
"""
	global PEERS

	try: cfg.__NETWORK__.update(NETWORKS.get(network))
	except: raise NetworkError("Unknown %s network properties" % network)	

	if network in ["testnet", "devnet"]:
		# in js month value start from 0, in python month value start from 1
		cfg.__BEGIN_TIME__ = datetime.datetime(2016, 5, 24, 17, 0, 0, 0, tzinfo=UTC)
		cfg.__NET__ = network
	else:
		# in js month value start from 0, in python month value start from 1
		cfg.__BEGIN_TIME__ = datetime.datetime(2017, 3, 21, 13, 0, 0, 0, tzinfo=UTC)
		cfg.__NET__ = "mainnet"

	seedlist = SEEDLIST.get(cfg.__NET__, [])
	if not len(seedlist):
		raise NetworkError("No seed defined for %s network" % network)
	peerlist = ["http://%(ip)s:%(port)s"%p for p in json.loads(requests.get(choose(seedlist)+"/api/peers", timeout=2).text).get("peers", []) if p["status"] == "OK"]
	if not len(peerlist):
		raise NetworkError("No peer available on %s network" % network)

	n = min(broadcast, len(peerlist))
	PEERS = peerlist if len(peerlist) == n else []
	while len(PEERS) < broadcast:
		peer = choose(peerlist)
		if peer not in PEERS:
			PEERS.append(peer)

	cfg.__URL_BASE__ = choose(peerlist)
	cfg.__HEADERS__.update({
		'Content-Type' : 'application/json; charset=utf-8',
		'os'           : 'arky',
		'version'      : __version__,
		'nethash'      : Block.getNethash().get("nethash", "")
	})

	sys.ps1 = "@%s>>> " % network
	sys.ps2 = "@%s... " % network

# initailize testnet by default
try: use()
except: pass
