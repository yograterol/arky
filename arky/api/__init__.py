# -*- encoding: utf8 -*-
# © Toons

# only GET method is implemented, no POST or PUT for security reasons
from .. import cfg, ArkyDict, choose, setInterval, NETWORKS
import sys, json, requests, traceback, datetime, pytz
UTC = pytz.UTC

class NetworkError(Exception): pass

# GET generic method for ARK API
def get(api, dic={}, **kw):
	returnkey = kw.pop("returnKey", False)
	try:
		text = requests.get(cfg.__URL_BASE__+api, params=dict(dic, **kw), timeout=5).text
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
			"http://188.165.177.41:4000",
		])

	else:
		# in js month value start from 0, in python month value start from 1
		cfg.__BEGIN_TIME__ = datetime.datetime(2017, 3, 21, 13, 0, 0, 0, tzinfo=UTC)
		cfg.__NET__ = "mainnet"
		cfg.__URL_BASE__ = choose([
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

@setInterval(500)
def rotatePeer():
	try: peer = choose(Peer.getPeersList().get("peers", []))
	except: peer = {}
	if "string" in peer:
		old_one = cfg.__URL_BASE__
		cfg.__URL_BASE__ = "http://" + peer["string"]
		try: success = Loader.getNethash().get("success", False)
		except: success = False
		if success: cfg.__LOG__.put({"API info": "using peer %s" % cfg.__URL_BASE__})
		else: cfg.__URL_BASE__ = old_one
