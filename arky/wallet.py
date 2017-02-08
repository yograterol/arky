# -*- encoding: utf8 -*-
# © Toons
from . import core, api, slots, ArkyDict, StringIO
import json, hashlib, binascii


class Wallet(object):

	# list of candidate a wallet can vote
	candidates = []
	# list of usernames already upvoted
	votes =   property(lambda obj: [d["username"] for d in api.Account.getVotes(obj.address).get("delegates", [])], None, None, "")
	# get total ARK in wallet
	balance = property(lambda obj: int(api.Account.getBalance(obj.address).get("balance", 0)), None, None, "")

# 	@staticmethod
# 	def open(filename):
# 		"""
# """
# 		in_ = open(filename, "r")
# 		serial = json.load(in_)
# 		in_.close()

# 		obj = Wallet()
# 		key_one = core.unserializeKeys(serial)
# 		object.__setattr__(obj._Wallet__tx, "key_one", key_one)
# 		object.__setattr__(obj._Wallet__tx, "address", core.getAddress(key_one))
# 		Wallet.init(obj)
# 		Wallet.update(obj)
# 		return obj

	@staticmethod
	def create(secret):
		pass
# Account.openAccount = function(secretKey, callback) {
#   Api.post({
#     url: options.url + '/api/accounts/open',
#     form: {
#       secret: secretKey
#     },
#     json: true
#   }, callback);
# };

	# def __init__(self, secret=None, secondSecret=None):
	# 	# self.__tx = core.Transaction()
	# 	if secret:
	# 		# self.__tx.secret = secret
	# 		self.init()
	# 		self.update()
	# 	if secondSecret:
	# 		self.__tx.secondSecret = secondSecret

	# def init(self):
	# 	public_key = binascii.hexlify(self.__tx.key_one.public)
	# 	self.publicKey = public_key.decode() if isinstance(public_key, bytes) else public_key
	# 	self.address = core.getAddress(self.__tx.key_one)
	# 	self.wif = self.__tx.key_one.wif

	# def update(self):
	# 	all_delegates = api.Delegate.getCandidates()
	# 	object.__setattr__(self, "delegate", bool(len([d for d in all_delegates[:51] if d['publicKey'] == self.publicKey])))
	# 	if self.delegate: object.__setattr__(self, "registered", True)
	# 	else: object.__setattr__(self, "registered", bool(len([d for d in all_delegates[51:] if d['publicKey'] == self.publicKey])))
	# 	Wallet.candidates = [d["username"] for d in all_delegates]

	def __setattr__(self, attr, value):
		if attr in["delegate", "registered"]:
			raise core.NotGrantedAttribute("%s can not be set through Wallet interface" % attr)
		object.__setattr__(self, attr, value)

	# def reset(self):
	# 	for attr in [a for a in core.Transaction.attr if hasattr(self.__tx, a)]:
	# 		delattr(self.__tx, attr)
	# 	self.__tx.type = 0
	# 	self.__tx.amount = 0
	# 	self.__tx.timestamp = slots.getTime()
	# 	self.__tx.asset = ArkyDict()

	def sendArk(self, secret, amount, recipientId, **kw):
		pass
		# self.reset()
		# self.__tx.amount = amount
		# self.__tx.recipientId = recipientId
		# for attr in [a for a in core.Transaction.attr if a in kw and a not in ["amount", "recipientId"]]:
		# 	setattr(self.__tx, attr, kw[attr])
		# return core.sendTransaction(secret, self.__tx)

	def registerAsDelegate(self, secret, username):
		pass
		# self.reset()
		# self.__tx.type = 2
		# self.__tx.asset.delegate = ArkyDict(username=username, publicKey=self.publicKey)
		# return core.sendTransaction(secret, self.__tx)

	def voteDelegate(self, secret, up=[], down=[]):
		# self.reset()
		votes = self.votes
		usernames = ['+'+c for c in up if c not in votes and c in Wallet.candidates] + \
		            ['-'+c for c in down if c in Wallet.candidates]
		# if len(usernames):
		# 	self.__tx.type = 3
		# 	self.__tx.recipientId = self.address
		# 	self.__tx.asset.votes = usernames
		# 	return core.sendTransaction(secret, self.__tx)

	def save(self, filename):
		in_ = open(filename, "w")
		json.dump(core.serializeKeys(self.__tx.key_one), in_, indent=2)
		in_.close()

#	registerSecondSingature(secondSign)
