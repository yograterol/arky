# -*- encoding: utf8 -*-
# © Toons

from ecdsa.keys import SigningKey
from ecdsa.util import sigencode_der
from ecdsa.curves import SECP256k1

from . import cfg #, cfg.__NETWORK__, cfg.__FEES__, cfg.__HEADERS__ cfg.__URL_BASE__
from . import __PY3__, StringIO, slots, ArkyDict
import base58, struct, hashlib, binascii, requests, json


# define core exceptions 
class NotGrantedAttribute(Exception): pass
class NoSecretDefinedError(Exception): pass
class NoSenderDefinedError(Exception): pass
class NotSignedTransactionError(Exception): pass
class StrictDerSignatureError(Exception): pass


# read value binary data from buffer
unpack = lambda fmt, fileobj: struct.unpack(fmt, fileobj.read(struct.calcsize(fmt)))
# write value binary data into buffer
pack =  lambda fmt, fileobj, value: fileobj.write(struct.pack(fmt, *value))
# write bytes as binary data into buffer
pack_bytes = lambda f,v: pack("<"+"%ss"%len(v), f, (v,)) if __PY3__ else \
             lambda f,v: pack("<"+"c"*len(v), f, v)


def use(net="testnet"):
	"""
select ARK net to use
>>> use("testnet") # use testnet (default)
>>> use("mainnet") # use testnet
"""

	if net == "mainnet":
		cfg.__URL_BASE__ = "http://node1.arknet.cloud:4000"
		cfg.__NETWORK__.update(
			messagePrefix = b"\x18Ark Signed Message:\n",
			bip32         = ArkyDict(public=0x043587cf, private=0x04358394),
			pubKeyHash    = b"\x6f",
			wif           = b"\xef",
		)
		cfg.__HEADERS__.update({
			'Content-Type': 'application/json; charset=utf-8',
			'os': 'arkwalletapp',
			'version': '0.5.0',
			'port': '1',
			'nethash': "ed14889723f24ecc54871d058d98ce91ff2f973192075c0155ba2b7b70ad2511"
		})

	elif net == "testnet":
		cfg.__URL_BASE__ = "http://node1.arknet.cloud:4000"
		cfg.__NETWORK__.update(
			messagePrefix = b"\x18Testnet Ark Signed Message:\n",
			bip32         = ArkyDict(public=0x0488b21e, private=0x0488ade4),
			pubKeyHash    = b"\x17",
			wif           = b"\xaa",
		)
		cfg.__HEADERS__.update({
			'Content-Type': 'application/json; charset=utf-8',
			'os': 'arkwalletapp',
			'version': '0.5.0',
			'port': '1',
			'nethash': "8b2e548078a2b0d6a382e4d75ea9205e7afc1857d31bf15cc035e8664c5dd038"
		})

	else:
		raise Exception("%s net properties not known" % net)

# activate testnet by default
use("testnet")


def _compressEcdsaPublicKey(pubkey):
	first, last = pubkey[:32], pubkey[32:]
	# check if last digit of second part is even (2%2 = 0, 3%2 = 1)
	even = not bool((last[-1] if __PY3__ else ord(last[-1])) % 2)
	return (b"\x02" if even else b"\x03") + first


def getKeys(secret="passphrase", seed=None, network=None):
	"""
Generate `keys` containing `network`, `public` and `private` key as attribute.
`secret` or `seed` have to be provided, if `network` is not, `cfg.__NETWORK__` is
automatically selected.

Keyword arguments:
secret (str or bytes) -- a human pass phrase
seed (byte)           -- a sha256 sequence bytes
network (object)      -- a python object

Returns ArkyDict
"""
	network = cfg.__NETWORK__ if network == None else network # use cfg.__NETWORK__ network by default
	seed = hashlib.sha256(secret.encode("utf8") if not isinstance(secret, bytes) else secret).digest() if not seed else seed

	keys = ArkyDict()
	# save wallet address
	keys.wif = getWIF(seed, network)
	# save network option
	keys.network = network
	# generate signing and verifying object and public key
	keys.signingKey = SigningKey.from_secret_exponent(int(binascii.hexlify(seed), 16), SECP256k1, hashlib.sha256)
	keys.checkingKey = keys.signingKey.get_verifying_key()
	keys.public = _compressEcdsaPublicKey(keys.checkingKey.to_string())

	return keys


def serializeKeys(keys):
	"""
Serialize `keys`.

Argument:
keys (ArkyDict) -- keyring returned by `getKeys`

Returns ArkyDict
"""
	skeys = ArkyDict()
	sk = binascii.hexlify(keys.signingKey.to_pem())
	skeys.signingKey = sk.decode() if isinstance(sk, bytes) else sk
	skeys.wif = keys.wif
	return skeys


def unserializeKeys(serial, network=None):
	"""
Unserialize serial.

Argument:
keys (dict) -- serialized keyring returned by `serializeKeys`

Returns ArkyDict ready to be used as keyring
"""
	keys = ArkyDict()
	keys.network = cfg.__NETWORK__ if network == None else network # use cfg.__NETWORK__ network by default
	keys.signingKey = SigningKey.from_pem(binascii.unhexlify(serial["signingKey"]))
	keys.checkingKey = keys.signingKey.get_verifying_key()
	keys.public = _compressEcdsaPublicKey(keys.checkingKey.to_string())
	keys.wif = serial["wif"]
	return keys


def getAddress(keys):
	"""
Computes ARK address from keyring.

Argument:
keys (ArkyDict) -- keyring returned by `getKeys`

Returns str
"""
	network = keys.network
	ripemd160 = hashlib.new('ripemd160', keys.public).digest()[:21]
	seed = network.pubKeyHash + ripemd160
	return base58.b58encode_check(seed)


def getWIF(seed, network):
	"""
Computes WIF address from keyring.

Argument:
seed (bytes)     -- a sha256 sequence bytes
network (object) -- a python object

Returns str
"""
	network = network
	compressed = network.get("compressed", True)
	seed = network.wif + seed[:32] + (b"\x01" if compressed else b"")
	return base58.b58encode_check(seed)


def getBytes(transaction):
	"""
Computes transaction object as bytes data.

Argument:
transaction (arky.core.Transaction) -- transaction object

Returns sequence bytes
"""
	buf = StringIO() # create a buffer

	# write type as byte in buffer
	pack("<b", buf, (transaction.type,))
	# write timestamp as integer in buffer (see if uint is better)
	pack("<i", buf, (int(transaction.timestamp),))
	# write senderPublicKey as bytes in buffer
	try:
		pack_bytes(buf, transaction.senderPublicKey)
	except AttributeError:
		raise NoSenderDefinedError("%r does not belong to any ARK account" % self)

	if hasattr(transaction, "requesterPublicKey"):
		pack_bytes(buf, transaction.requesterPublicKey)

	if hasattr(transaction, "recipientId"):
		# decode reciever adress public key
		recipientId = base58.b58decode_check(transaction.recipientId)
	else:
		# put a blank
		recipientId = b"\x00"*21
	pack_bytes(buf,recipientId)

	if hasattr(transaction, "vendorField"):
		# put vendor field value (64 bytes limited)
		n = min(64, len(transaction.vendorField))
		vendorField = transaction.vendorField[:n].encode() + b"\x00"*(64-n)
	else:
		# put a blank
		vendorField = b"\x00"*64
	pack_bytes(buf, vendorField)

	# write amount value
	pack("<Q", buf, (transaction.amount,))
	pack("<Q", buf, (transaction.fee,))

	# more test to confirm the good bytification of type 1 to 4...
	typ  = transaction.type
	if typ == 1 and "signature" in transaction.asset:
		pack_bytes(buf, transaction.asset.signature)
	elif typ == 2 and "delegate" in transaction.asset:
		pack_bytes(buf, transaction.asset.delegate.username.encode())
	elif typ == 3 and "votes" in transaction.asset:
		pack_bytes(buf, ("".join(transaction.asset.votes)).encode())
	elif typ == 4 and "multisignature" in transaction.asset:
		pack("<b", buf, (transaction.asset.multisignature.min,))
		pack("<b", buf, (transaction.asset.multisignature.lifetime,))
		pack_bytes(buf, ("".join(transaction.asset.multisignature.keysgroup)).encode())

	# if there is a signature
	if hasattr(transaction, "signature"):
		pack_bytes(buf, transaction.signature)
	
	# if there is a second signature
	if hasattr(transaction, "signSignature"):
		pack_bytes(buf, transaction.signSignature)

	result = buf.getvalue()
	buf.close()
	return result.encode() if not isinstance(result, bytes) else result


def checkStrictDER(sig):
	"""
https://github.com/bitcoin/bips/blob/master/bip-0066.mediawiki#der-encoding-reference
Check strict DER signature compliance.

Argument:
sig (bytes) -- signature sequence bytes

Raises StrictDerSignatureError exception or return sig
"""
	sig_len = len(sig)
	# Extract the length of the R element.
	r_len = sig[3]
	# Extract the length of the S element.
	s_len = sig[5+r_len]

	# Minimum and maximum size constraints.
	if 8 > sig_len > 72:
		raise StrictDerSignatureError("bad signature size (<8 or >72)")
	# A signature is of type 0x30 (compound).
	if sig[0] != 0x30:
		raise StrictDerSignatureError("A signature is not of type 0x30 (compound)")
	# Make sure the length covers the entire signature.
	if sig[1] != (sig_len - 2):
		raise StrictDerSignatureError("length %d does not covers the entire signature (%d)" % (sig[1], sig_len))
	# Make sure the length of the S element is still inside the signature.
	if (5 + r_len) >= sig_len:
		raise StrictDerSignatureError("S element is not inside the signature")
	# Verify that the length of the signature matches the sum of the length of the elements.
	if (r_len + s_len + 6) != sig_len:
		raise StrictDerSignatureError("signature length does not matches sum of the elements")
	# Check whether the R element is an integer.
	if sig[2] != 0x02:
		raise StrictDerSignatureError("R element is not an integer")
	# Zero-length integers are not allowed for R.
	if r_len == 0:
		raise StrictDerSignatureError("Zero-length is not allowed for R element")
	# Negative numbers are not allowed for R.
	if sig[4] & 0x80:
		raise StrictDerSignatureError("Negative number is not allowed for R element")
	# Null bytes at the start of R are not allowed, unless R would otherwise be interpreted as a negative number.
	if r_len > 1 and sig[4] == 0x00 and not sig[5] & 0x80:
		raise StrictDerSignatureError("Null bytes at the start of R element is not allowed")
	# Check whether the S element is an integer.
	if sig[r_len+4] != 0x02:
		raise StrictDerSignatureError("S element is not an integer")
	# Zero-length integers are not allowed for S.
	if s_len == 0:
		raise StrictDerSignatureError("Zero-length is not allowed for S element")
	# Negative numbers are not allowed for S.
	if sig[r_len+6] & 0x80:
		raise StrictDerSignatureError("Negative number is not allowed for S element")
	# Null bytes at the start of S are not allowed, unless S would otherwise be interpreted as a negative number.
	if s_len > 1 and sig[r_len+6] == 0x00 and not sig[r_len+7] & 0x80:
		raise StrictDerSignatureError("Null bytes at the start of S element is not allowed")
	return sig


class Transaction(object):
	r'''
Transaction object is the core of the API. This object is a container with smart
behaviour according to attribute value that are settled in. 

Attributes that can be set using object interface :
type               (int)
amount             (int)
timestamp          (float)
asset              (ArkyDict)
secret             (str)
vendorField        (str)
recipientId        (str)
requesterPublicKey (str)

Public address attribute can only be set by secret passphrase, there are three way to do it:
>>> import arky.core as core
>>> tx1 = core.Transaction(secret="secret") # first way
>>> tx1.address
'AJWRd23HNEhPLkK1ymMnwnDBX2a7QBZqff'
>>> tx2 = core.Transaction()
>>> tx2.address = 'AJWRd23HNEhPLkK1ymMnwnDBX2a7QBZqff'
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "C:\Users\Bruno\Python\../GitHub/arky\arky\core.py", line 268, in __setattr__
    self.amount = kwargs.pop("amount", 0)
arky.core.NotGrantedAttribute: address attribute can not be set using object interface
>>> tx2.secret = 'secret'                   # second way
>>> tx2.address
'AJWRd23HNEhPLkK1ymMnwnDBX2a7QBZqff'
>>> tx3 = core.Transaction()
>>> tx3.sign(secret)                        # third way
>>> tx3.address
'AJWRd23HNEhPLkK1ymMnwnDBX2a7QBZqff'

Note that if secret is set, signature is done so:
>>> tx1.sing()
>>> tx2.sign()

If no secret defined:
>>> bad_tx = core.Transaction()
>>> bad_tx.sign()
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "C:\Users\Bruno\Python\../GitHub/arky\arky\core.py", line 316, in sign
    raise NoSecretDefinedError("No secret defined for %r" % self)
arky.core.NoSecretDefinedError: No secret defined for <0.00000000 ARK unsigned Transaction from "No one" to "No one">
'''
	# here are attribute that can be set through object interface
	attr = ["type", "amount", "timestamp", "asset", "vendorField", "secret", "recipientId", "requesterPublicKey"]
	senderPublicKey = property(lambda obj:obj.key_one.public, None, None, "alias for public key, read-only attribute")

	def __init__(self, **kwargs):
		# the four minimum attributes that defines a transaction
		self.type = kwargs.pop("type", 0)
		self.amount = kwargs.pop("amount", 0)
		self.timestamp = slots.getTime()
		self.asset = kwargs.pop("asset", ArkyDict())
		for attr,value in kwargs.items():
			setattr(self, attr, value)

	def __setattr__(self, attr, value):
		if attr not in Transaction.attr:
			raise NotGrantedAttribute("%s attribute can not be set using object interface" % attr)
		# if one of granted attribute is modified, it change signature in-fine
		# so unsign transaction to delete id, signature and signSignature
		self._unsign()
		if attr == "secret":
			# secret is not stored
			# associated ecdsa object and ARK address are instead
			keys = getKeys(value)
			object.__setattr__(self, "key_one", keys)
			object.__setattr__(self, "address", getAddress(keys))
		elif attr == "secondSecret":
			# second secret is not stored
			# associated ecdsa object is instead
			object.__setattr__(self, "key_two", getKeys(value))
		elif attr == "type":
			# when doing `<object>.type = value` automaticaly set the associated fees
			if value == 0:   object.__setattr__(self, "fee", cfg.__FEES__.send)
			elif value == 1: object.__setattr__(self, "fee", cfg.__FEES__.secondsignature)
			elif value == 2: object.__setattr__(self, "fee", cfg.__FEES__.delegate)
			elif value == 3: object.__setattr__(self, "fee", cfg.__FEES__.vote)
			elif value == 4: object.__setattr__(self, "fee", cfg.__FEES__.multisignature)
			elif value == 5: object.__setattr__(self, "fee", cfg.__FEES__.get("ipfs", 0))
			object.__setattr__(self, attr, value)
		else:
			object.__setattr__(self, attr, value)

	def __del__(self):
		if hasattr(self, "key_one"): delattr(self, "key_one")
		if hasattr(self, "key_two"): delattr(self, "key_two")

	def __repr__(self):
		return "<%(amount).8f ARK %(signed)s Transaction from %(from)s to %(to)s>" % {
			"signed": "signed" if hasattr(self, "signature") else \
			          "double-signed" if hasattr(self, "signSignature") else \
			          "unsigned",
			"amount": self.amount//100000000,
			"from": getattr(self, "address", '"No one"'),
			"to": getattr(self, "recipientId", '"No one"')
		}

	def _unsign(self):
		if hasattr(self, "signature"): delattr(self, "signature")
		if hasattr(self, "signSignature"): delattr(self, "signSignature")
		if hasattr(self, "id"): delattr(self, "id")

	def sign(self, secret=None):
		if secret != None:
			self.secret = secret
		elif not hasattr(self, "key_one"):
			raise NoSecretDefinedError("No secret defined for %r" % self)
		self._unsign()
		stamp = getattr(self, "key_one").signingKey.sign_deterministic(getBytes(self), hashlib.sha256, sigencode_der)
		object.__setattr__(self, "signature", checkStrictDER(stamp))
		object.__setattr__(self, "id", hashlib.sha256(getBytes(self)).digest())

	def seconSign(self, secondSecret=None):
		if not hasattr(self, "signature"):
			raise NotSignedTransactionError("%r must be signed first" % self)
		if secondSecret != None:
			self.secondSecret = secondSecret
		elif not hasattr(self, "key_two"):
			raise NoSecretDefinedError("No second secret defined for %r" % self)
		if hasattr(self, "signSignature"): delattr(self, "signSignature")
		stamp = getattr(self, "key_two").signingKey.sign_deterministic(getBytes(self), hashlib.sha256, sigencode=sigencode_der)
		object.__setattr__(self, "signSignature", checkStrictDER(stamp))
		object.__setattr__(self, "id", hashlib.sha256(getBytes(self)).digest())

	def serialize(self):
		data = ArkyDict()
		for attr in [a for a in [
			"id", "timestamp", "type", "fee", "amount", 
			"recipientId", "senderPublicKey", "requesterPublicKey", "vendorField",
			"asset", "signature", "signSignature"
		] if hasattr(self, a)]:
			value = getattr(self, attr)
			if isinstance(value, bytes):
				value = binascii.hexlify(value)
				if isinstance(value, bytes):
					value = value.decode()
			elif attr in ["amount", "timestamp", "fee"]: value = int(value)
			setattr(data, attr, value)
		return data


def sendTransaction(secret, transaction, n=10, secondSignature=None):
	attempt = 0
	while n: # yes i know, it is brutal :)
		transaction.sign(secret)
		if secondSignature:
			transaction.seconSign(secondSignature)
		result = ArkyDict(json.loads(requests.post(
			cfg.__URL_BASE__+"/peer/transactions",
			data=json.dumps({"transactions": [transaction.serialize()]}),
			headers=cfg.__HEADERS__
		).text))
		if result["success"]:
			break
		else:
			n -= 1
			attempt += 1
			# 1s shift timestamp for hash change
			transaction.timestamp -= 1

	result.attempt = attempt
	return result


def sendMultiple(secret, *transactions, **kw):
	result = ArkyDict()
	i = 1
	for transaction in transactions:
		data = sendTransaction(secret, transaction, n=kw.get("n", 10), secondSignature=kw.get('secondSinature', None))
		if data['success']:
			key = data.pop('transactionId')
			result[key] = data
		else:
			result["tx%03d" % i] = data
		i += 1
	return result
