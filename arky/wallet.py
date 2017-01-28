# -*- encoding: utf8 -*-
# © Toons
from . import core, api, slots, ArkyDict
import hashlib, binascii


class Wallet(object):

	# list of candidate a wallet can vote
	candidates = []
	# list of usernames already upvoted
	votes =   property(lambda obj: [d["username"] for d in api.Account.getVotes(obj.address).get("delegates", [])], None, None, "")
	# get total ARK in wallet
	balance = property(lambda obj: int(api.Account.getBalance(obj.address).get("balance", 0)), None, None, "")

	def __init__(self, secret, secondSecret=None):
		self.__tx = core.Transaction(secret=secret)
		if secondSecret: self.__tx.secondSecret = secondSecret

		public_key = binascii.hexlify(self.__tx.key_one.public)
		self.publicKey = public_key.decode() if isinstance(public_key, bytes) else public_key
		self.address = core.getAddress(self.__tx.key_one)
		self.wif = self.__tx.key_one.wif

		self.update()

	def update(self):
		all_delegates = api.Delegate.getCandidates()
		object.__setattr__(self, "delegate", bool(len([d for d in all_delegates[:51] if d['publicKey'] == self.publicKey])))
		if self.delegate: object.__setattr__(self, "registered", True)
		else: object.__setattr__(self, "registered", bool(len([d for d in all_delegates[51:] if d['publicKey'] == self.publicKey])))
		Wallet.candidates = [d["username"] for d in all_delegates]

	def __setattr__(self, attr, value):
		if attr in["delegate", "registered"]:
			raise core.NotGrantedAttribute("%s can not be set through Wallet interface" % attr)
		object.__setattr__(self, attr, value)

	def reset(self):
		for attr in core.Transaction.attr:
			if hasattr(self.__tx, attr):
				delattr(self.__tx, attr)
		self.__tx.type = 0
		self.__tx.amount = 0
		self.__tx.timestamp = slots.getTime()
		self.__tx.asset = ArkyDict()

	def sendArk(self, secret, amount, recipientId, **kw):
		self.reset()
		self.__tx.amount = amount
		self.__tx.recipientId = recipientId
		for attr in [a for a in core.Transaction.attr if a in kw and a not in ["amount", "recipientId"]]:
			setattr(self.__tx, attr, kw[attr])
		return core.sendTransaction(secret, self.__tx)

	def voteDelegate(self, secret, up=[], down=[]):
		self.reset()
		votes = self.votes
		usernames = ['+'+c for c in up if c not in votes and c in Wallet.candidates] + \
		            ['-'+c for c in down if c in Wallet.candidates]
		if len(usernames):
			self.__tx.type = 3
			self.__tx.recipientId = self.address
			self.__tx.asset.votes = usernames
			return core.sendTransaction(secret, self.__tx)

	def registerAsDelegate(self, secret, username):
		self.reset()
		self.__tx.type = 2
		self.__tx.asset.delegate = ArkyDict(username=username, publicKey=self.publicKey)
		return core.sendTransaction(secret, self.__tx)

	def serialize(self):
		return self.__tx.serialize()

#	registerSecondSingature(secondSign)
