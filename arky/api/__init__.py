# -*- encoding: utf8 -*-
# © Toons

# only GET method is implemented, no POST or PUT for security reasons
from .. import cfg, core, ArkyDict, choose, setInterval, NETWORKS, SEEDLIST, __version__
import os, sys, json, requests, traceback, datetime, random, pytz
UTC = pytz.UTC

# define api exceptions 
class TransactionError(Exception): pass
class NetworkError(Exception): pass
class SeedError(Exception): pass
class PeerError(Exception): pass


def get(api, dic={}, **kw):
	"""
ARK API call using requests lib. It returns server response as ArkyDict object.
It uses default peer registered in cfg.__URL_BASE__ variable.

Argument:
api (str) -- api url path

Keyword argument:
dic (dict) -- api parameters as dict type
**kw       -- api parameters as keyword argument (overwriting dic ones)

Returns ArkyDict
"""
	# merge dic and kw values
	args = dict(dic, **kw)
	# API response contains several fields and wanted one can be extracted using
	# a returnKey that match the field name
	returnKey = args.pop("returnKey", False)
	args = dict([k.replace("and_", "AND:") if k.startswith("and_") else k, v] for k,v in args.items())
	try:
		text = requests.get(cfg.__URL_BASE__+api, params=args, headers=cfg.__HEADERS__, timeout=3).text
		data = ArkyDict(json.loads(text))
	except Exception as error:
		data = ArkyDict({"success":False, "error":error})
		data.error = error
		if hasattr(error, "__traceback__"):
			data.details = "\n"+("".join(traceback.format_tb(error.__traceback__)).rstrip())
	else:
		if data.success:
			data = data[returnKey] if returnKey in data else data
	return data

def _signTx(tx, secret=None, secondSecret=None):
	if not secret:
		try: return tx.sign()
		except core.NoSecretDefinedError: return tx
	else:
		return tx.sign(secret, secondSecret)

def sendTx(tx, secret=None, secondSecret=None, url_base=None):
	"""
Send backed transaction using optional url_base and eventualy secrets. It
returns server response as ArkyDict object. If secrets are given, transaction is
signed and then broadcasted with signatures and id. It does not send secrets.

Argument:
tx (core.Transaction | list | tuple) -- transaction object(s) to be send

Keyword argument:
url_base     (str) -- the base api url to use
secret       (str) -- secret of the account sending the transaction
secondSecret (str) -- second secret of account sending the transaction

Returns ArkyDict
"""
	# use registered peer if no url_base is given
	if url_base == None: url_base = cfg.__URL_BASE__

	if isinstance(tx, (list, tuple)):
		tx = [_signTx(t, secret, secondSecret) for t in tx]
	elif isinstance(tx, core.Transaction):
		tx = [_signTx(tx, secret, secondSecret)]
	else:
		raise TransactionError("Can not send %r into blockchain" % tx)
	transactions = json.dumps({"transactions": [t.serialize() for t in tx if t]})

	try:
		text = requests.post(url_base + "/peer/transactions", data=transactions, headers=cfg.__HEADERS__, timeout=3).text
		data = ArkyDict(json.loads(text))
	except Exception as error:
		data = ArkyDict({"success":False, "error":error})
		if hasattr(error, "__traceback__"):
			data.details = "\n"+("".join(traceback.format_tb(error.__traceback__)).rstrip())
	else:
		if data.success:
			data.transaction = "%r" % tx
	return data

def broadcast(tx, secret=None, secondSecret=None):
	"""
Send transaction using multiple peers. It avoid broadcasting errors when large
amount of peers are unresponsive or not up to date.

Argument:
tx (core.Transaction | list | tuple) -- transaction object(s) to be send

Keyword argument:
secret       (str) -- secret of the account sending the transaction
secondSecret (str) -- second secret of account sending the transaction

Returns ArkyDict
"""
	result = sendTx(tx, secret, secondSecret)
	ratio = 0.
	if result.success:
		for peer in PEERS:
			if sendTx(tx, secret, secondSecret, peer).success: ratio += 1
	result.broadcast = "%.1f%%" % (ratio/len(PEERS)*100)
	return result

def checkPeerLatency(peer, timeout=3):
	try: r = requests.get(peer + '/api/blocks/getNethash', timeout=timeout)
	except: return False
	else: return r.elapsed.total_seconds()

def use(network="devnet", broadcast=7, custom_seed=None, latency=1):
	"""
Select ARK network.

Keyword argument:
network   (str) -- network name you want to connetc with
broadcast (int) -- max valid peer number to use for broadcasting

Returns None
"""
	global PEERS

	try: cfg.__NETWORK__.update(NETWORKS.get(network))
	except: raise NetworkError("Unknown %s network properties" % network)

	# in js month value start from 0, in python month value start from 1
	cfg.__BEGIN_TIME__ = datetime.datetime(2017, 3, 21, 13, 0, 0, 0, tzinfo=UTC)
	cfg.__NET__ = network if network in ["testnet", "devnet"] else "mainnet"

	# find seeds
	if custom_seed:
		seedlist = [custom_seed]
	else:
		seedlist = SEEDLIST.get(cfg.__NET__, [])
	if not len(seedlist):
		sys.ps1 = "@offline>>> "
		sys.ps2 = "@offline... "
		cfg.__NET__ = "offline"
		return

	# select a valid seed
	seed, nb_try = None, 0
	while not seed and nb_try < 10:
		temp = choose(seedlist)
		if checkPeerLatency(temp, timeout=latency):
			seed = temp
		nb_try += 1
	if not seed:
		sys.ps1 = "@offline>>> "
		sys.ps2 = "@offline... "
		cfg.__NET__ = "offline"
		return

	# get all valid peers
	api_peers = []
	while not len(api_peers):
		try: 
			api_peers = json.loads(requests.get(seed+"/api/peers", timeout=3).text).get("peers", [])
		except requests.exceptions.ConnectionError:
			sys.ps1 = "@offline>>> "
			sys.ps2 = "@offline... "
			cfg.__NET__ = "offline"
			return
	peerlist = []
	goodpeers = ["http://%(ip)s:%(port)s"%p for p in api_peers if p["status"] == "OK"]
	random.shuffle(goodpeers)

	# select a set of peers for transaction broadcasting
	for peer in goodpeers:
		if checkPeerLatency(peer, timeout=latency): peerlist.append(peer)
		if len(peerlist) == broadcast: break
	if not len(peerlist):
		sys.ps1 = "@offline>>> "
		sys.ps2 = "@offline... "
		cfg.__NET__ = "offline"
		return
	PEERS = peerlist

	# finish network conf
	cfg.__URL_BASE__ = choose(peerlist) if not custom_seed else custom_seed
	cfg.__HEADERS__.update({
		'Content-Type' : 'application/json; charset=utf-8',
		'os'           : 'arky',
		'port'         : '1',
		'version'      : __version__,
		'nethash'      : Block.getNethash().get("nethash", "")
	})

	sys.ps1 = "@%s>>> " % network
	sys.ps2 = "@%s... " % network

#################
## API wrapper ##
#################

class Loader:

	@staticmethod
	def getLoadingStatus(**param):
		return get('/api/loader/status', **param)

	@staticmethod
	def getSynchronisationStatus(**param):
		return get('/api/loader/status/sync', **param)


class Block:

	@staticmethod
	def getBlocks(**param):
		return get('/api/blocks', **param)

	@staticmethod
	def getBlock(blockId, **param):
		return get('/api/blocks/get', id=blockId, **param)

	@staticmethod
	def getNethash(**param):
		return get('/api/blocks/getNethash', **param)

	@staticmethod
	def getBlockchainFee(**param):
		return get('/api/blocks/getFee', **param)

	@staticmethod
	def getBlockchainHeight(**param):
		return get('/api/blocks/getHeight', **param)

	@staticmethod
	def getForgedByAccount(publicKey, **param):
		return get('/api/delegates/forging/getForgedByAccount', generatorPublicKey=publicKey, **param)


class Account:

	@staticmethod
	def getBalance(address, **param):
		return get('/api/accounts/getBalance', address=address, **param)

	@staticmethod
	def getPublicKey(address, **param):
		return get('/api/accounts/getPublicKey', address=address, **param)

	@staticmethod
	def getAccount(address, **param):
		return get('/api/accounts', address=address, **param)

	@staticmethod
	def getVotes(address, **param):
		return get('/api/accounts/delegates', address=address, **param)


class Delegate:

	@staticmethod
	def getDelegates(**param):
		return get('/api/delegates', **param)

	@staticmethod
	def getDelegate(username, **param):
		return get('/api/delegates/get', username=username, **param)

	@staticmethod
	def getVoters(publicKey, **param):
		return get('/api/delegates/voters', publicKey=publicKey, **param)

	@staticmethod
	def getCandidates(**param):
		delegates = []
		while 1:
			found = Delegate.getDelegates(offset=len(delegates), limit=51, **param).get("delegates", [])
			delegates += found
			if len(found) < 51:
				break
		return delegates


class Transaction(object):

	@staticmethod
	def getTransactionsList(**param):
		return get('/api/transactions', **param)

	@staticmethod
	def getUnconfirmedTransactions(**param):
		return get('/api/transactions/unconfirmed', **param)

	@staticmethod
	def getTransaction(transactionId, **param):
		return get('/api/transactions/get', id=transactionId, **param)

	@staticmethod
	def getUnconfirmedTransaction(transactionId, **param):
		return get('/api/transactions/unconfirmed/get', id=transactionId, **param)


class Peer:

	@staticmethod
	def getPeersList(**param):
		return get('/api/peers', **param)

	@staticmethod
	def getPeer(ip, port, **param):
		return get('/api/peers', ip=ip, port=port, **param)

	@staticmethod
	def getPeerVersion(**param):
		return get('/api/peers/version', **param)


class Multisignature:

	@staticmethod
	def getPendingMultiSignatureTransactions(publicKey, **param):
		return get('/api/multisignatures/pending', publicKey=publicKey, **param)

	@staticmethod
	def getAccountsOfMultisignature(publicKey, **param):
		return post('/api/multisignatures/accounts', publicKey=publicKey, **param)

use(broadcast=10)
