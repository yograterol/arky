# -*- encoding: utf8 -*-
# © Toons

'''
    This command allows escrow account creation and management. Account is
    shared between owner, who initiates transactions, and escrower, who
    validates and broadcast transactions.

    Owner holds secret passphrase, escrower holds second secret one.

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
from .. import ArkyDict, ROOT, core, api, cfg
from . import common

import binascii, hashlib, base58, shlex, json, sys, io, os

ADDRESS = None
PUBLICKEY = None
KEY1 = None
KEY2 = None

TOKENS = os.path.normpath(os.path.join(ROOT, ".token"))
try: os.makedirs(TOKENS)
except: pass

def register(param):
	if _checkKey1():
		tx = common.generateColdTx(KEY1, PUBLICKEY, type=1, asset=ArkyDict(signature=ArkyDict(publicKey=param["<2ndPublicKey>"])))
		common.prettyPrint(api.broadcastSerial(tx), log=True)

def publickey(param):
	keys = core.getKeys(param["<secret>"])
	pubkey = common.hexlify(keys.public)
	sys.stdout.write("Here is the public key: %s\nSend this bublic key as is to the account owner\n" % pubkey)

def link(param):
	global KEY1, KEY2, PUBLICKEY, ADDRESS

	if param["--escrow"]:
		if param["<secret>"]:
			KEY2 = core.getKeys(param["<secret>"]).signingKey
		else:
			try: choices = [os.path.splitext(name)[0] for name in os.listdir(os.path.join(TOKENS, cfg.__NET__)) if name.endswith(".tok2")]
			except: choices = []
			if choices:
				KEY2 = _load2ndToken(_2ndTokenPath(common.chooseItem("Second signature account(s) found:", *choices)))
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
			try: choices = [os.path.splitext(name)[0] for name in os.listdir(os.path.join(TOKENS, cfg.__NET__)) if name.endswith(".tok1")]
			except: choices = []
			if choices:
				ADDRESS, PUBLICKEY, KEY1 = _load1stToken(_1stTokenPath(common.chooseItem("First signature account(s) found:", *choices)))
			else:
				sys.stdout.write("No first-token found\n")
		KEY2 = None

def send(param):
	if _checkKey1():
		amount = common.floatAmount(param["<amount>"], ADDRESS)*100000000
		if amount:
			tx = common.generateColdTx(KEY1, PUBLICKEY, type=0, amount=amount, recipientId=param["<address>"], vendorField=param["<message>"])
		else:
			tx = False
		if tx:
			tx.address = ADDRESS
			sys.stdout.write("You can now give %s file to your escrow\n" % common.dropColdTx(tx))

def validate(param):
	if KEY2:
		if param["<id>"]:
			tx = common.loadColdTx(param["<id>"])
		else:
			choices = [os.path.splitext(name)[0] for name in os.listdir(os.path.join(common.COLDTXS, cfg.__NET__)) if name.endswith(".ctx")]
			if choices:
				tx = common.loadColdTx(common.chooseItem("Cold transaction(s) found:", *choices))
		if tx:
			tmp = core.signSerial(tx, KEY2)
			tx.update({"id":tmp["id"], "signSignature":tmp["signature"]})
			if common.askYesOrNo("Broadcast %s?" % common.reprColdTx(tx)):
				common.prettyPrint(api.broadcastSerial(tx), log=True)
			else:
				sys.stdout.write("Broadcast canceled\n")
		else:
			sys.stdout.write("%s Cold transaction not found\n" % tx.id)

def save(param):
	if KEY1 and PUBLICKEY and ADDRESS: _drop1stToken(_1stTokenPath(param["<name>"]), ADDRESS, PUBLICKEY, KEY1)
	elif KEY2: _drop2ndToken(_2ndTokenPath(param["<name>"]), KEY2)

def unlink(param):
	global KEY1, KEY2, PUBLICKEY, ADDRESS
	KEY1, KEY2, PUBLICKEY, ADDRESS = None, None, None, None


# --------------
def _whereami():
	if ADDRESS:
		return "escrow[%s]" % common.shortAddress(ADDRESS)
	elif KEY2:
		k2 = binascii.hexlify(KEY2.to_string())
		k2 = k2.decode() if isinstance(k2, bytes) else k2
		return "escrow[%s]" % (common.shortAddress(k2))
	else: return "escrow"

def _sk2Hex(signingKey):
	return common.hexlify(signingKey.to_pem())

def _hex2Sk(hexa):
	return SigningKey.from_pem(common.unhexlify(hexa))

def _checkKey1():
	if not KEY1:
		sys.stdout.write("No account linked\n")
		return False
	return True

def _1stTokenPath(name):
	global TOKENS
	name = name.decode() if isinstance(name, bytes) else name
	if not name.endswith(".tok1"): name += ".tok1"
	return os.path.join(TOKENS, cfg.__NET__, name)

def _drop1stToken(filename, address, publicKey, signingKey):
	common.checkFolderExists(filename)
	out = io.open(filename, "w")
	out.write("%s%s%s" % (address, common.hexlify(publicKey), _sk2Hex(signingKey)))
	out.close()

def _load1stToken(filename):
	in_ = io.open(filename, "r")
	data = in_.read()
	in_.close()
	return (data[:34], common.unhexlify(data[34:34+66]), _hex2Sk(data[34+66:]))

def _2ndTokenPath(name):
	global TOKENS
	name = name.decode() if isinstance(name, bytes) else name
	if not name.endswith(".tok2"): name += ".tok2"
	return os.path.join(TOKENS, cfg.__NET__, name)

def _drop2ndToken(filename, signingKey):
	common.checkFolderExists(filename)
	out = io.open(filename, "w")
	out.write(_sk2Hex(signingKey))
	out.close()

def _load2ndToken(filename):
	in_ = io.open(filename, "r")
	data = in_.read()
	in_.close()
	return _hex2Sk(data)
