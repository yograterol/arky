# -*- encoding: utf8 -*-
# © Toons

from ecdsa.keys import SigningKey
from arky import ArkyDict
from arky import core, slots

import binascii, logging, hashlib, random, base58, sys, imp, os

def _prettyDic(dic, tab="    "):
	result = ""
	if len(dic):
		maxlen = max([len(e) for e in dic.keys()])
		for k,v in dic.items():
			if isinstance(v, dict):
				result += tab + "%s:" % k.ljust(maxlen)
				result += _prettyDic(v, tab*2)
			else:
				result += tab + "%s: %s" % (k.ljust(maxlen),v)
			result += "\n"
		return result

def _prettyPrint(dic, tab="    "):
	if len(dic): sys.stdout.write(_prettyDic(dic, tab))
	else: sys.stdout.write("Nothing to print here\n")

def _prettyLog(dic, tab="    "):
	if len(dic): logging.info(_prettyDic(dic, tab))
	else: logging.info("Nothing to log here")

def getAccountKeyValues(secret):
	keys = core.getKeys(secret)
	spk = binascii.hexlify(keys.public)
	sk = binascii.hexlify(keys.signingKey.to_pem())
	ck = binascii.hexlify(keys.checkingKey.to_pem())
	return {
		"spk": spk.decode() if isinstance(spk, bytes) else spk,
		"sk": sk.decode() if isinstance(sk, bytes) else sk,
		"ck": ck.decode() if isinstance(ck, bytes) else ck
	}

def registerSecondSignature(secondSecret, senderPublicKey, signingKey):
	#new publicKey for second signature
	npk = binascii.hexlify(core.getKeys(secondSecret).public)
	npk = npk.decode() if isinstance(npk, bytes) else npk

	# preparing key_oneobject needed for tx signature
	key_one =ArkyDict()
	spk = binascii.unhexlify(senderPublicKey)
	spk = spk if isinstance(spk, bytes) else spk.encode()
	sk= SigningKey.from_pem(binascii.unhexlify(signingKey))
	key_one.public = spk
	key_one.signingKey = sk
	
	# create tx
	tx = core.Transaction(type=1, asset=ArkyDict(signature=ArkyDict(publicKey=npk)))
	object.__setattr__(tx, "key_one", key_one)
	result = core.api.broadcast([tx])

	_prettyPrint(result)

# def scrambleData(senderPublicKey, signingKey):
# 	nb_elem = random.randint(3, 7)
# 	# 03a5789a4486f20f1fdca78a52b528b3bf9952e7c057de71a22adcfb444ba4c5d3
# 	# 03a5789a4486f20f1fdca78a52b528b3bf9952e7c057de71a22adcfb444ba4c5d3
# 	# 02c7b92a2d0027309e21855cf9c42a432b21ad13925e9dfc206f9c01e18fefa08a
# 	slices = []
# 	for i in range(nb_elem):
# 		slices[i] = random.randint(11, 33)
# 	slices[-1] = sum(66 - slices[:-1])
# 	print(sum(slices), "should be == 66")


# 	pass

# def unscrambleData(scramble):
# 	pass

