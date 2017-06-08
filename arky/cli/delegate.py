# -*- encoding: utf8 -*-
# © Toons

#        delegate support <amount> [<message>]
#        delegate fidelity <days>
#     fidelity : show fidelity of voters for a certain day history.
#     support  : share ARK amount to relay nodes according to their vote rate.
#                You can set a 64-char message.

'''
Usage: delegate link [<secret>]
       delegate save <name>
       delegate unlink
       delegate status
       delegate voters
       delegate share <amount> [-b <blacklist> -d <delay> <message>]

Options:
-b <blacklist> --blacklist <blacklist> comma-separated ark addresse list
-a <address> --address <address>       already linked ark address
-k <keyring> --keyring <keyring>       a valid *.akr pathfile
-d <delay> --delay <delay>             number of fidelity-day            [default: 30]

Subcommands:
    link     : link to account using secret passphrases, Ark address or
               *.tokd file. If secret passphrases contains spaces, it must be
               enclosed within double quotes ("secret with spaces"). Note
               that you can use address only for *.tokd files registered
               locally.
    save     : save linked delegate to an *.tokd file.
    unlink   : unlink account.
    status   : show information about linked account.
    voters   : show voters contributions ([address - vote] pairs).
    share    : share ARK amount with voters (if any) according to their
               weight. You can set a 64-char message.
'''

from ecdsa.keys import SigningKey
from .. import cfg, api, core, ROOT
from ..util import stats
from . import common

try:
	from . import _share
	SHARE = True
except: 
	SHARE = False

import io, os, sys

ADDRESS = None
PUBLICKEY = None
KEY1 = None
KEY2 = None
USERNAME = None
DELEGATE = None

TOKENS = os.path.normpath(os.path.join(ROOT, ".token"))
try: os.makedirs(TOKENS)
except: pass

def link(param):
	global ADDRESS, PUBLICKEY, KEY1, KEY2, USERNAME, DELEGATE
	
	if param["<secret>"]:
		keys = core.getKeys(param["<secret>"])
		KEY1 = keys.signingKey
		PUBLICKEY = keys.public
		ADDRESS = core.getAddress(keys)

	else:
		try: choices = [os.path.splitext(name)[0] for name in os.listdir(os.path.join(TOKENS, cfg.__NET__)) if name.endswith(".tokd")]
		except: choices = []
		if choices:
			ADDRESS, PUBLICKEY, KEY1 = _loadDgtToken(_DgtTokenPath(common.chooseItem("Delegate account(s) found:", *choices)))

	USERNAME = _checkIfDelegate()
	if not USERNAME:
		sys.stdout.write("Not a delegate\n")
		ADDRESS, PUBLICKEY, KEY1, KEY2, USERNAME, DELEGATE = None, None, None, None, None, None

def save(param):
	if KEY1 and PUBLICKEY and ADDRESS:
		_dropDgtToken(_DgtTokenPath(param["<name>"]), ADDRESS, PUBLICKEY, KEY1)

def unlink(param):
	global ADDRESS, PUBLICKEY, KEY1, KEY2, USERNAME, DELEGATE
	ADDRESS, PUBLICKEY, KEY1, KEY2, USERNAME, DELEGATE = None, None, None, None, None, None

def status(param):
	if ADDRESS:
		common.prettyPrint(dict(DELEGATE, **api.Account.getAccount(ADDRESS, returnKey="account")))

def voters(param):
	if PUBLICKEY:
		accounts = api.Delegate.getVoters(common.hexlify(PUBLICKEY), returnKey="accounts")
		sum_ = 0.
		for addr, vote in ([c["address"],float(c["balance"])/100000000] for c in accounts):
			line = "    %s: %.3f\n" % (addr, vote)
			sys.stdout.write(line)
			sum_ += vote
		sys.stdout.write("    " + "-"*(len(line)-4) + "\n")
		sys.stdout.write("    %s: %.3f\n" % (("%d voters"%len(accounts)).rjust(len(addr)), sum_))

def share(param):
	if PUBLICKEY and SHARE:
		accounts = api.Delegate.getVoters(common.hexlify(PUBLICKEY), returnKey="accounts")
		if param["--blacklist"]:
			if os.path.exists(param["--blacklist"]):
				with io.open(param["--blacklist"], "r") as in_:
					blacklist = in_.read().split()
			else:
				blacklist = param["--blacklist"].split(",")
		else:
			blacklist = []

		delay = int(param["--delay"])
		sys.stdout.write("Checking %s-day-true-vote-weight on transaction history...\n" % delay)
		contributions = dict([address, stats.getVoteForce(address, delay)] for address in [a["address"] for a in accounts if a["address"] not in blacklist])
		k = 1.0/max(1, sum(contributions.values()))
		contributions = dict((a, round(s*k, 6)) for a,s in contributions.items())

		if _checkSecondSignature():
			txgen = lambda addr,amnt,msg: common.generateColdTx(KEY1, PUBLICKEY, KEY2, type=0, amount=amnt, recipientId=addr, vendorField=msg)
			_share.applyContribution(common.floatAmount(param["<amount>"], ADDRESS), param["<message>"], txgen, **contributions)

# --------------
def _checkSecondSignature():
	global KEY2

	secondPublickKey = api.Account.getAccount(ADDRESS, returnKey="account").get('secondPublickKey', None)
	if secondPublickKey:
		keys = core.getKeys(getpass.getpass("Enter second passphrase: "))
		spk = common.hexlify(keys.public)
		if spk == secondPublicKey:
			return True
			KEY2 = keys.signingKey
		else:	
			sys.stdout.write("Incorrect second passphrase, operation canceled !\n")
			return False
	else:
		KEY2 = None
		return True

def _whereami():
	if USERNAME:
		return "delegate[%s]" % USERNAME
	else:
		return "delegate"

def _sk2Hex(signingKey):
	return common.hexlify(signingKey.to_pem())

def _hex2Sk(hexa):
	return SigningKey.from_pem(common.unhexlify(hexa))

def _checkKey1():
	if not KEY1:
		sys.stdout.write("No account linked\n")
		return False
	return True

def _checkIfDelegate():
	global DELEGATE
	search = [d for d in api.Delegate.getCandidates() if d['publicKey'] == common.hexlify(PUBLICKEY)]
	if len(search):
		DELEGATE = search[0]
		return DELEGATE["username"]
	else:
		return None

def _DgtTokenPath(name):
	global TOKENS
	name = name.decode() if isinstance(name, bytes) else name
	if not name.endswith(".tokd"): name += ".tokd"
	return os.path.join(TOKENS, cfg.__NET__, name)

def _dropDgtToken(filename, address, publicKey, signingKey):
	common.checkFolderExists(filename)
	out = io.open(filename, "w")
	out.write("%s%s%s" % (address, common.hexlify(publicKey), _sk2Hex(signingKey)))
	out.close()

def _loadDgtToken(filename):
	in_ = io.open(filename, "r")
	data = in_.read()
	in_.close()
	return (data[:34], common.unhexlify(data[34:34+66]), _hex2Sk(data[34+66:]))
