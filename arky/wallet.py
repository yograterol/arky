# -*- encoding: utf8 -*-
# © Toons

from . import cfg, api, mgmt, core, slots, ArkyDict, StringIO, setInterval, HOME, __PY3__
import io, json, socket, hashlib, binascii, logging, threading
if __PY3__: raw_input = input

# define wallet exceptions 
class ReadOnlyAttributes(Exception): pass
class SecondSignatureError(Exception): pass
class MultiSignatureError(Exception): pass


class Wallet(object):
	r'''
Wallet object allows user to send all type of transaction granted by the Ark blockchain.

Attributes that can be set using object interface :
secret       (str) -- a valid utf-8 encoded string
secondSecret (str) -- a valid utf-8 encoded string

>>> from arkyimport wallet
>>> w = wallet.Wallet("secret")
>>> w.address
'a3T1iRdHFt35bKY8RX1bZBGbenmmKZ12yR'
>>> w.wif
'cP3giX8Vmcev97Y5BvMH1kPteesGk3AQ9vd9ifyis5r5sFiV8H26'
>>> w.publicKey
'03a02b9d5fdd1307c2ee4652ba54d492d1fd11a7d1bb3f3a44c4a05e79f19de933'
>>> w.delegates[1]
{'vote': '254644554598363', 'missedblocks': 17, 'productivity': 98.23, 'rate': 2, 'addres\
s': 'AMLLuYLAfM4VWzzFxE8P5gFnof8JDpSgrm', 'approval': 2.04, 'username': 'arky', 'publicKe\
y': '0211fe5bf889735fb982bb04ffeed0e7a46f781201d8bba5bc2daed6411a6b8348', 'producedblocks\
': 942}
>>> w.sendArk(1.5, 'aPzezL8FFR3gnJC3hyJ6V1eFeFRNUzsS4y', "A1.5 for you using arky API")
>>> w.registerAsDelegate("secret_delegate")
>>> w.voteDelegate(up=["arky", "ravelou"])
>>> w.votes
['ravelou', 'arky']
>>> w.voteDelegate(down=["arky"])
>>> w.votes
['ravelou']
'''

	# list of all registered delegates
	delegates = api.Delegate.getCandidates()
	# list of delegate usernames a wallet can vote
	candidates = []
	# list of votes done through wallet
	votes = property(lambda obj: [d["username"] for d in api.Account.getVotes(obj.address).get("delegates", [])], None, None, "")
	# list of voters given to wallet
	voters = property(lambda obj: api.Delegate.getVoters(obj.publicKey).get("accounts", []), None, None, "")
	# return voter contribution ratio
	contribution = property(lambda obj: getVoterContribution(obj), None, None, "")
	# return wallet balance in ARK
	balance = property(lambda obj: int(obj.account.get("balance", 0))/100000000., None, None, "")
	# return wallet WIF addres
	wif = property(lambda obj: obj.K1.wif, None, None, "")

	def __init__(self, secret=None, secondSecret=None):
		if secret:
			self.secret = secret
			if self.account.get('secondSignature', False):
				if secondSecret:
					self.secondSecret = secondSecret
				else:
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
			@setInterval(15)
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
		self._stop_check_daemon.set()
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
		Wallet.delegates = api.Delegate.getCandidates()
		Wallet.candidates = [d["username"] for d in Wallet.delegates]

	def _generate_tx(self, **kw):
		"""
Generate a transaction with wallet key(s)
"""
		tx = core.Transaction(**kw)
		object.__setattr__(tx, "key_one", self.K1)
		object.__setattr__(tx, "address", core.getAddress(self.K1))
		if hasattr(self, "K2"):
			object.__setattr__(tx, "key_two", self.K2)
		return tx

	def sendArk(self, amount, recipientId, vendorField=None):
		"""
Send ARK amount to recipientId.

Argument:
amount      (float) -- amount you want to send in ARK (not in SATOSHI !)
recipientId (str) -- valid ARK address you want to send to
vendorField (str) -- 64-char-max message you want to send with (None by default)
"""
		mgmt.push(self._generate_tx(type=0, amount=int(amount*100000000.), recipientId=recipientId, vendorField=vendorField))

	# experimental... do not use. working on LAN for now
	def sendMultisignArk(self, amount, recipientId, **kw):
		keysgroup = kw.pop("keysgroup", [])
		if len(keysgroup) < 1: raise MultiSignatureError()

		ip = kw.pop("ip", cfg.__IP__)
		port = kw.pop("port", cfg.__PORT__)
		lifetime = kw.pop("lifetime", 72)
		minimum = kw.pop("minimum", min(len(keysgroup), 2))
		timeout = kw.pop("timeout", 2*60) # 2 minutes

		asset = ArkyDict(multisignature=ArkyDict(min=minimum, lifetime=lifetime, keysgroup=[("+"+k if k[0] not in ["+","-"] else k) for k in keysgroup]))
		tx = self._generate_tx(type=4, amount=int(amount*100000000.), recipientId=recipientId, asset=asset, **kw)
		object.__setattr__(tx, "fee", tx.fee*(minimum+1))
		tx.sign()

		q = cfg.queue.Queue()
		s = socket.socket()
		s.bind(("", port))
		s.listen(minimum)
		print("listening signal, ip:port = %s:%s" % (ip, port))

		data = json.dumps(tx.serialize())
		data = data.encode() if not isinstance(data, bytes) else data

		threads = []
		for i in range(minimum):
			conn, addr = s.accept()
			conn.settimeout(timeout)
			print(conn)
			print("remote %s:%s accepted connection" % addr)
			t = threading.Thread(target=askRemoteSignature, args=(conn, data, q))
			t.daemon = True # stop if the program exits
			t.start()
			threads.append(t)

		for t in threads: t.join()
		s.close()

		object.__setattr__(tx, "signatures", [str(sig.decode() if isinstance(sig, bytes) else sig) for sig in q.queue if len(sig) > 0])
		mgmt.push(tx)

	# experimental... do not use. working on LAN for now
	def remoteSign(self, ip, port):
		s = socket.socket()
		s.connect((ip, port))
		data = s.recv(1024)
		data = json.loads(data.decode() if isinstance(data, bytes) else data)
		for item in sorted(data.items(), key=lambda e:e[0]): print("%s : %s" % item)
		if raw_input(">>> sign this transaction [y/n]: ") in ["Y", "y", "yes"]:
			s.sendall(core.signSerial(data, self.K1))
		s.close()

	def voteDelegate(self, up=[], down=[]):
		"""
Up or down vote for delegates. Delegates name are listed in `wallet.candidates` attribute.
Automatically filters usernames that are already voted up/down ore are invalid.

Argument:
up   (list) -- list of username to be upvoted
down (list) -- list of username to be downvoted
"""
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
			mgmt.push(self._generate_tx(type=3, recipientId=self.address, asset=ArkyDict(votes=usernames)))
		else:
			cfg.__LOG__.put({"API info": "no one to up/down vote"})

	def registerAsDelegate(self, username):
		"""
Register wallet as a delegate (this enables forging).

Arguments:
username (str) -- a utf-8 valid username
"""
		if not self.delegate:
			mgmt.push(self._generate_tx(type=2, asset=ArkyDict(delegate=ArkyDict(username=username, publicKey=self.publicKey))))
		else:
			cfg.__LOG__.put({"API info": "%s already registered as delegate" % self.publicKey})

	def registerSecondSignature(self, secondSecret):
		"""
Register a second signature. This is permanent and the two secrets have to be given to
open the wallet. When second signature is registered on blockchain side, it automatically
register the second key into the wallet.

Argument:
secondSecret (str) -- a valid utf-8 encoded string
"""
		if not self.account.get('secondSignature'):
			newPublicKey = binascii.hexlify(core.getKeys(secondSecret).public)
			newPublicKey = newPublicKey.decode() if isinstance(newPublicKey, bytes) else newPublicKey
			mgmt.push(self._generate_tx(type=1, asset=ArkyDict(signature=ArkyDict(publicKey=newPublicKey))))
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


def getVoterContribution(wlt):
	data = {}
	total_votes = float(wlt.delegate["vote"])
	for voter in wlt.voters:
		voter_addr = voter["address"]
		nb_votes = len(api.Account.getVotes(voter_addr).get("delegates", []))
		if nb_votes > 0:
			data[voter_addr] = round(float(voter['balance'])/nb_votes/total_votes, 3)
	return data

# used by Wallet.sendMultisignArk
def askRemoteSignature(conn, data, q):
	conn.sendall(data)
	sig = conn.recv(1024)
	q.put(binascii.hexlify(sig))
	conn.close()


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
	
	@setInterval(15)
	def _check(o): obj.update()
	obj._stop_check_daemon = _check(obj)

	return obj

