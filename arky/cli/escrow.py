# -*- encoding: utf8 -*-
# © Toons

#        escrow vote [-u <delegate>... | -d <delegate>...]
#     vote      : up or/and down vote delegates from linked account
# -u --up      up vote all delegates name folowing
# -d --down    down vote all delegates name folowing

'''
Usage: escrow register <2ndPublicKey>
       escrow publickey <secret>
       escrow link [<secret> -e]
       escrow send <amount> <address> [<message>]
       escrow validate [<id>]
       escrow save <name>
       escrow unlink

Options:
-e --escrow  tag that allow user link as an escrower

Subcommands:
    register  : set double-signature account using escrow public key
    publickey : return the public key from secret
    link      : link account to create or validate transactions
    send      : create cold transaction to send ARK if validated
    validate  : broadcast cold transactions
    save      : save account locally
    unlink    : unlink from account
'''

from ecdsa.keys import SigningKey
from .. import ArkyDict, ROOT, core, cfg
from .common import floatAmount, prettyPrint, chooseItem

import binascii, hashlib, base58, shlex, json, sys, io, os

ADDRESS = None
PUBLICKEY = None
KEY1 = None
KEY2 = None

TOKENS = os.path.normpath(os.path.join(ROOT, ".token"))
try: os.makedirs(TOKENS)
except: pass

COLDTXS = os.path.normpath(os.path.join(ROOT, ".coldtx"))
try: os.makedirs(COLDTXS)
except: pass

def publickey(param):
	keys = core.getKeys(param["<secret>"])
	pubkey = _hexlify(keys.public)
	sys.stdout.write("Here is the public key: %s\nSend this bublic key as is to the account owner\n" % pubkey)

def register(param):
	if _checkKey1():
		tx = _generateColdTx(type=1, asset=ArkyDict(signature=ArkyDict(publicKey=param["<2ndPublicKey>"])))
		if tx:
			tx.sign()
			prettyPrint(_broadcastSerial(tx.serialize()), log=True)

def unlink(param):
	global KEY1, KEY2, PUBLICKEY, ADDRESS
	KEY1, KEY2, PUBLICKEY, ADDRESS = None, None, None, None

def save(param):
	if KEY1 and PUBLICKEY and ADDRESS: _drop1stToken(_1stTokenPath(param["<name>"]), ADDRESS, PUBLICKEY, KEY1)
	elif KEY2: _drop2ndToken(_2ndTokenPath(param["<name>"]), KEY2)

def link(param):
	global KEY1, KEY2, PUBLICKEY, ADDRESS

	if param["--escrow"]:
		if param["<secret>"]:
			KEY2 = core.getKeys(param["<secret>"]).signingKey
		else:
			choices = [os.path.splitext(name)[0] for name in os.listdir(os.path.join(TOKENS, cfg.__NET__)) if name.endswith(".tok2")]
			if choices:
				KEY2 = _load2ndToken(_2ndTokenPath(chooseItem("Second signature account(s) found:", *choices)))
			else:
				sys.stdout.write("No second-tokend found\n")
		KEY1 = None
		PUBLICKEY = None
		ADDRESS = None

	else:
		if param["<secret>"]:
			keys = core.getKeys(param["<secret>"])
			KEY1 = keys.signingKey
			PUBLICKEY = keys.public
			ADDRESS = core.getAddress(keys)
		else:
			choices = [os.path.splitext(name)[0] for name in os.listdir(os.path.join(TOKENS, cfg.__NET__)) if name.endswith(".tok1")]
			if choices:
				ADDRESS, PUBLICKEY, KEY1 = _load1stToken(_1stTokenPath(chooseItem("First signature account(s) found:", *choices)))
			else:
				sys.stdout.write("No first-token found\n")
		KEY2 = None

def send(param):
	if _checkKey1():
		tx = _generateColdTx(
			type=0, 
			amount=floatAmount(param["<amount>"], ADDRESS)*100000000, 
			recipientId=param["<address>"], 
			vendorField=param["<message>"])
		if tx:
			tx.sign()
			tx = tx.serialize()
			tx.address = ADDRESS
			sys.stdout.write("You can now give %s file to your escrow\n" % os.path.basename(_dropColdTx(tx)))

def validate(param):
	global KEY2

	if KEY2:
		if param["<id>"]:
			filename = os.path.join(COLDTXS, cfg.__NET__, param["<id>"] + ".ctx")
			tx = _loadColdTx(filename)
		else:
			choices = [os.path.splitext(name)[0] for name in os.listdir(os.path.join(COLDTXS, cfg.__NET__)) if name.endswith(".ctx")]
			if choices:
				tx = _loadColdTx(os.path.join(COLDTXS, cfg.__NET__, chooseItem("Cold transaction(s) found:", *choices)+".ctx"))
		if tx:
			tmp = core.signSerial(tx, KEY2)
			tx.update({"id":tmp["id"], "signSignature":tmp["signature"]}) #core.signSerial(tx, KEY2))
			prettyPrint(_broadcastSerial(tx), log=True)
		else:
			sys.stdout.write("%s Cold transaction not found\n" % tx.id)


# ----------
def _shortAddress(addr, sep="...", n=5):
	return addr[:n]+sep+addr[-n:]

def _reprColdTx(ctx):
	pass

def _whereami():
	if ADDRESS:
		return "escrow[%s]" % _shortAddress(ADDRESS)
	elif KEY2:
		k2 = binascii.hexlify(KEY2.to_string())
		k2 = k2.decode() if isinstance(k2, bytes) else k2
		return "escrow[%s]" % (_shortAddress(k2))
	else: return "escrow"

def _sk2Hex(signingKey):
	return _hexlify(signingKey.to_pem())

def _hex2Sk(hexa):
	return SigningKey.from_pem(_unhexlify(hexa))

def _checkFolderExists(filename):
	folder = os.path.dirname(filename)
	if not os.path.exists(folder):
		os.makedirs(folder)

def _hexlify(data):
	result = binascii.hexlify(data)
	return result.decode() if isinstance(result, bytes) else result

def _unhexlify(data):
	result = binascii.unhexlify(data)
	return result if isinstance(result, bytes) else result.encode()

def _checkKey1():
	if not KEY1:
		sys.stdout.write("No account linked\n")
		return False
	return True

def _1stTokenPath(filename):
	global TOKENS
	filename = filename.decode() if isinstance(filename, bytes) else filename
	if not filename.endswith(".tok1"): filename += ".tok1"
	return os.path.join(TOKENS, cfg.__NET__, filename)

def _drop1stToken(filename, address, publicKey, signingKey):
	_checkFolderExists(filename)
	out = io.open(filename, "w")
	out.write("%s%s%s" % (address, _hexlify(publicKey), _sk2Hex(signingKey)))
	out.close()

def _load1stToken(filename):
	in_ = io.open(filename, "r")
	data = in_.read()
	in_.close()
	return (data[:34], _unhexlify(data[34:34+66]), _hex2Sk(data[34+66:]))

def _2ndTokenPath(filename):
	global TOKENS
	filename = filename.decode() if isinstance(filename, bytes) else filename
	if not filename.endswith(".tok2"): filename += ".tok2"
	return os.path.join(TOKENS, cfg.__NET__, filename)

def _drop2ndToken(filename, signingKey):
	_checkFolderExists(filename)
	out = io.open(filename, "w")
	out.write(_sk2Hex(signingKey))
	out.close()

def _load2ndToken(filename):
	in_ = io.open(filename, "r")
	data = in_.read()
	in_.close()
	return _hex2Sk(data)

def _generateColdTx(**kw):
	global KEY1, PUBLICKEY
	if KEY1 and PUBLICKEY:
		tx = core.Transaction(**kw)
		object.__setattr__(tx, "key_one", ArkyDict(public=PUBLICKEY, signingKey=KEY1))
		return tx
	else:
		sys.stdout.write("Can not create cold transaction\n")
		return False

def _dropColdTx(tx):
	global COLDTXS, ADDRESS
	filename = os.path.join(COLDTXS, cfg.__NET__, "%s.ctx" % tx.id)
	_checkFolderExists(filename)
	if isinstance(tx, core.Transaction): tx = tx.serialize()
	out = io.open(filename, "w")
	json.dump(tx, out, indent=2)
	out.close()
	return filename

def _loadColdTx(filename):
	if os.path.exists(filename):
		in_ = io.open(filename, "r")
		tx = json.load(in_)
		in_.close()
		return tx
	else:
		return False
	
def _postData(url_base, data):
	return json.loads(
		core.api.requests.post(
			url_base + "/peer/transactions",
			data=data,
			headers=cfg.__HEADERS__,
			timeout=3
		).text
	)

def _broadcastSerial(serial):
	data = json.dumps({"transactions": [serial]})
	result = _postData(cfg.__URL_BASE__, data)
	ratio = 0.
	if result["success"]:
		for peer in core.api.PEERS:
			if _postData(peer, data)["success"]: ratio += 1
	result["broadcast"] = "%.1f%%" % (ratio/len(core.api.PEERS)*100)
	return result
