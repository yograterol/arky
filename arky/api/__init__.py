# -*- encoding: utf8 -*-
# © Toons

# only GET method is implemented, no POST or PUT for security reasons
from .. import ArkyDict, cfg
import json, requests, traceback

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
