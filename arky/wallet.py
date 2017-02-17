# -*- encoding: utf8 -*-
# © Toons

from . import cfg, api, mgmt, core, slots, ArkyDict, StringIO, setInterval, HOME
import io, json, hashlib, binascii, logging

# define wallet exceptions 
class ReadOnlyAttributes(Exception): pass
class SecondSignatureError(Exception): pass


class Wallet(object):
	r'''
Wallet object allows user to send all type of transaction granted by the Ark blockchain.

Attributes that can be set using object interface :
secret             (str)
secondSecret       (str)
'''

	# list of all registered delegates
	delegates = api.Delegate.getCandidates()
	# list of delegate usernames a wallet can vote
	candidates = []
	# list of votes done through wallet
	votes = property(lambda obj: [d["username"] for d in api.Account.getVotes(obj.address).get("delegates", [])], None, None, "")
	# list of voters given to wallet
	voters = property(lambda obj: api.Delegate.getVoters(obj.publicKey).get("accounts", []), None, None, "")

	balance = property(lambda obj: int(obj.account.get("balance", 0)), None, None, "")
	wif = property(lambda obj: obj.K1.wif, None, None, "")

	def __init__(self, secret=None, secondSecret=None):
		if secret:
			self.secret = secret
			if secondSecret:
				self.secondSecret = secondSecret
			elif self.account.get('secondSignature', False):
				raise SecondSignatureError("Missing second signature for this wallet")

	def __setattr__(self, attr, value):
		if attr in ["delegate", "registered", "forger", "K1", "K2", "account"]:
			raise ReadOnlyAttributes("%s can not be set through Wallet interface" % attr)
		elif attr == "secret":
			keys = core.getKeys(value)
			public_key = binascii.hexlify(keys.public)
			object.__setattr__(self, "address", core.getAddress(keys))
			object.__setattr__(self, "publicKey", public_key.decode() if isinstance(public_key, bytes) else public_key)
			object.__setattr__(self, "K1", keys)
			self.update()
			@setInterval(30)
			def _check(obj): obj.update()
			self._stop_check_daemon = _check(self)
		elif attr == "secondSecret":
			if self.account.get('secondSignature', False):
				keys = core.getKeys(value)
				keys.pop("wif")
				object.__setattr__(self, "K2", keys)
			else:
				raise SecondSignatureError("Second signature is registered to this wallet")
		object.__setattr__(self, attr, value)

	def __del__(self):
		self._stop_update_daemon.set()
		if hasattr(self, "_stop_setter_daemon"):
			self._stop_setter_daemon.set()

	def save(self, filename):
		in_ = io.open(filename, "w")
		sK1 = core.serializeKeys(self.K1)
		sK2 = core.serializeKeys(self.K2) if hasattr(self, "K2") else None
		json.dump([sK1, sK2], in_, indent=2)
		in_.close()

	def update(self):
		search = [d for d in Wallet.delegates if d['publicKey'] == self.publicKey]
		search51 = [d for d in Wallet.delegates[:51] if d['publicKey'] == self.publicKey]
		object.__setattr__(self, "delegate", search[0] if len(search) else False)
		object.__setattr__(self, "forger", True if len(search51) else False)
		object.__setattr__(self, "account", api.Account.getAccount(self.address).get("account", {}))

	def transaction(self, **kw):
		tx = core.Transaction(**kw)
		object.__setattr__(tx, "key_one", self.K1)
		object.__setattr__(tx, "address", core.getAddress(self.K1))
		if hasattr(self, "K2"):
			object.__setattr__(tx, "key_two", self.K2)
		return tx

	def sendArk(self, amount, recipientId, **kw):
		mgmt.push(self.transaction(type=0, amount=int(amount*100000000), recipientId=recipientId, **kw))

	def voteDelegate(self, up=[], down=[]):
		votes = self.votes
		# first filter
		up   = [u for u in up if u not in votes and u in Wallet.candidates]
		down = [u for u in down if u in votes]
		#second filter
		up = [d1['publicKey'] for d1 in [d0 for d0 in Wallet.delegates if d0['username'] in up]]
		down = [d1['publicKey'] for d1 in [d0 for d0 in Wallet.delegates if d0['username'] in down]]
		# concatenate votes
		usernames = ['+'+c for c in up] + ['-'+c for c in down]
		# send votes
		if len(usernames):
			mgmt.push(self.transaction(type=3, recipientId=self.address, asset=ArkyDict(votes=usernames)))
		else:
			cfg.__LOG__.put({"API info": "no one to up/down vote"})

	def registerAsDelegate(self, username):
		if not self.delegate:
			mgmt.push(self.transaction(type=2, asset=ArkyDict(delegate=ArkyDict(username=username, publicKey=self.publicKey))))
		else:
			cfg.__LOG__.put({"API info": "%s already registered as delegate" % self.publicKey})

	def registerSecondSingature(self, secondSecret):
		if not self.account.get('secondSignature'):
			newPublicKey = binascii.hexlify(core.getKeys(secondSecret).public)
			newPublicKey = newPublicKey.decode() if isinstance(newPublicKey, bytes) else newPublicKey
			mgmt.push(self.transaction(type=1, asset=ArkyDict(signature=ArkyDict(publicKey=newPublicKey))))
			# automaticaly set secondSignature when transaction is applied
			@setInterval(10)
			def _setter(obj, passphrase):
				try: obj.secondSecret = passphrase
				except SecondSignatureError: pass
				else:
					obj._stop_setter_daemon.set()
					delattr(obj, "_stop_setter_daemon")
					cfg.__LOG__.put({"API info": "Second signature set for %s" % self})
			if hasattr(self, "_stop_setter_daemon"):
				self._stop_setter_daemon.set()
				delattr(obj, "_stop_setter_daemon")
			self._stop_setter_daemon = _setter(self, secondSecret)
		else:
			cfg.__LOG__.put({"API info": "second signature already registered to %s" % self.publicKey})


def open(filename):
	in_ = io.open(filename, "r")
	K1, K2 = json.load(in_)
	in_.close()

	obj = Wallet()
	K1 = core.unserializeKeys(K1)
	public_key = binascii.hexlify(K1.public)
	object.__setattr__(obj, "address", core.getAddress(K1))
	object.__setattr__(obj, "publicKey", public_key.decode() if isinstance(public_key, bytes) else public_key)
	object.__setattr__(obj, "K1", K1)
	obj.update()
	if K2: object.__setattr__(obj, "K2", core.unserializeKeys(K2))
	return obj


@setInterval(60)
def check():
	# cfg.__LOG__.put({"API info": "loading delegates and candidates"})
	Wallet.delegates = api.Delegate.getCandidates()
	Wallet.candidates = [d["username"] for d in Wallet.delegates]
_stop_check_daemon = check()
