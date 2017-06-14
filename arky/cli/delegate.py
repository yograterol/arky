# -*- encoding: utf8 -*-
# © Toons

'''
Usage: delegate link [<secret>]
       delegate save <name>
       delegate unlink
       delegate status
       delegate voters
       delegate share <amount> [-c -b <blacklist> -d <delay> -l <lowest> -h <highest> <message>]

Options:
-b <blacklist> --blacklist <blacklist> comma-separated ark addresses to exclude
-h <highest> --highest <hihgest>       maximum payout in ARK
-l <lowest> --lowest <lowest>          minimum payout in ARK
-d <delay> --delay <delay>             number of fidelity-day [default: 30]
-c --complement                        share the amount complement

Subcommands:
    link   : link to delegate using secret passphrases. If secret passphrases
             contains spaces, it must be enclosed within double quotes
             ("secret with spaces"). If no secret given, it tries to link
             with saved account(s).
    save   : save linked delegate to a *.tokd file.
    unlink : unlink delegate.
    status : show information about linked delegate.
    voters : show voters contributions ([address - vote] pairs).
    share  : share ARK amount with voters (if any) according to their
             weight. You can set a 64-char message. (1% mandatory fees)
'''

from .. import cfg, api, core, ROOT
from .. util import stats
from . import common


import io, os, sys

SHARE = False
ADDRESS = None
PUBLICKEY = None
KEY1 = None
KEY2 = None
USERNAME = None
DELEGATE = None

try:
	from . import pshare
	SHARE = True
except ImportError:
	SHARE = False

def link(param):
	global ADDRESS, PUBLICKEY, KEY1, KEY2, USERNAME, DELEGATE
	
	if param["<secret>"]:
		keys = core.getKeys(param["<secret>"].encode("ascii"))
		KEY1 = keys.signingKey
		PUBLICKEY = keys.public
		ADDRESS = core.getAddress(keys)
		USERNAME = _checkIfDelegate()

	else:
		choices = common.findTokens("tokd")
		if choices:
			ADDRESS, PUBLICKEY, KEY1 = common.loadToken(common.tokenPath(common.chooseItem("Delegate account(s) found:", *choices), "tokd"))
			USERNAME = _checkIfDelegate()

	if not USERNAME:
		sys.stdout.write("Not a delegate\n")
		ADDRESS, PUBLICKEY, KEY1, KEY2, USERNAME, DELEGATE = None, None, None, None, None, None

def save(param):
	if KEY1 and PUBLICKEY and ADDRESS:
		common.dropToken(common.tokenPath(param["<name>"], "tokd"), ADDRESS, PUBLICKEY, KEY1)

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
	if _checkKey1():
		if SHARE:
			if param["--blacklist"]:
				if os.path.exists(param["--blacklist"]):
					with io.open(param["--blacklist"], "r") as in_:
						blacklist = in_.read().split()
				else:
					blacklist = param["--blacklist"].split(",")
			else:
				blacklist = []

			amount = common.floatAmount(param["<amount>"], ADDRESS)
			if param["--complement"]:
				amount = float(api.Account.getBalance(ADDRESS, returnKey="balance"))/100000000. - amount

			KEY2 = common.askSecondSignature(ADDRESS)
			if KEY2 != False and amount > 1:
				delay = int(param["--delay"])
				sys.stdout.write("Checking %s-day-true-vote-weight in transaction history...\n" % delay)
				accounts = api.Delegate.getVoters(common.hexlify(PUBLICKEY), returnKey="accounts")
				contributions = dict([address, stats.getVoteForce(address, delay)] for address in [a["address"] for a in accounts if a["address"] not in blacklist])
				k = 1.0/max(1, sum(contributions.values()))
				contributions = dict((a, round(s*k, 6)) for a,s in contributions.items())
				txgen = lambda addr,amnt,msg: common.generateColdTx(KEY1, PUBLICKEY, KEY2, type=0, amount=amnt, recipientId=addr, vendorField=msg)
				
				if param["--lowest"] : minimum = float(param["--lowest"])
				else: minimum = 0.
				if param["--highest"] : maximum = float(param["--highest"])
				else: maximum = amount
				pshare.applyContribution(USERNAME, amount, minimum, maximum, param["<message>"], txgen, **contributions)

		else:
			sys.stdout.write("Share feature not available\n")

# --------------
def _whereami():
	if USERNAME:
		return "delegate[%s]" % USERNAME
	else:
		return "delegate"

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
