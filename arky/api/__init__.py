# -*- encoding: utf8 -*-
# © Toons

# only GET method is implemented, no POST or PUT for security reasons
from .. import cfg, ArkyDict, choose, NETWORKS
import sys, json, requests, traceback, datetime, pytz
UTC = pytz.UTC

class NetworkError(Exception): pass

# GET generic method for ARK API
def get(api, dic={}, **kw):
	returnkey = kw.pop("returnKey", False)
	try:
		text = requests.get(cfg.__URL_BASE__+api, params=dict(dic, **kw)).text
		data = json.loads(text)
	except Exception as error:
		if hasattr(error, "__traceback__"):
			cfg.__LOG__.put({
				"API error": error,
				"details": "\n"+("".join(traceback.format_tb(error.__traceback__)).rstrip())
			})
		else:
			cfg.__LOG__.put({"API error": error})
	else:
		if data["success"]:
			return ArkyDict(data[returnkey]) if returnkey else ArkyDict(data)
	return ArkyDict()


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
	def getDelegates(offset=0):
		return get('/api/delegates', offset=offset)

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
			found = Delegate.getDelegates(offset=len(delegates)).get("delegates", [])
			delegates += found
			if len(found) < 51: break
		return delegates


class Transaction(object):

	@staticmethod
	def getTransactionsList():
		return get('/api/transactions')

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


def use(network="testnet"):
	"""
select ARK net to use
>>> use("ark") # use testnet
>>> cfg.__NET__
'mainnet'
>>> use("bitcoin2") # use testnet
Traceback (most recent call last):
...
NetworkError: Unknown bitcoin2 network properties
"""
	try: cfg.__NETWORK__.update(NETWORKS.get(network))
	except: raise NetworkError("Unknown %s network properties" % network)

	sys.ps1 = "@%s>>> " % network
	sys.ps2 = "@%s... " % network
	
	if network in ["testnet", "devnet"]:
		# in js month value start from 0, in python month value start from 1
		cfg.__BEGIN_TIME__ = datetime.datetime(2016, 5, 24, 17, 0, 0, 0, tzinfo=UTC)
		cfg.__NET__ = network
		cfg.__URL_BASE__ = choose([
			"http://5.39.9.245:4000",
			"http://5.39.9.246:4000",
			"http://5.39.9.247:4000",
			"http://5.39.9.248:4000",
			"http://5.39.9.249:4000"
		] if network == "testnet" else [
			"http://167.114.29.42:4000"
		])
	else:
		# in js month value start from 0, in python month value start from 1
		cfg.__BEGIN_TIME__ = datetime.datetime(2017, 2, 21, 19, 0, 0, 0, tzinfo=UTC)
		cfg.__NET__ = "mainnet"
		cfg.__URL_BASE__ = choose([
			"http://5.39.9.245:4000",
			"http://5.39.9.246:4000",
			"http://5.39.9.247:4000",
			"http://5.39.9.248:4000",
			"http://5.39.9.249:4000"
		])

	cfg.__HEADERS__.update({
		'Content-Type' : 'application/json; charset=utf-8',
		'os'           : 'arkwalletapp',
		'version'      : '0.5.0',
		'port'         : '1',
		'nethash'      : Block.getNethash().get("nethash", "")
	})
# initailize testnet by default
use("testnet")
