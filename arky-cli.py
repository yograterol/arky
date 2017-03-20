# -*- encoding: utf8 -*-
# © Toons

__version__ = "1.0"

from arky import cfg, api, core, wallet, ArkyDict, __PY3__, setInterval
from arky.util import getArkPrice
from docopt import docopt
import os, sys, imp, shlex, traceback, binascii, logging

input = raw_input if not __PY3__ else input 

# return True if it runs from a frozen script (py2exe, cx_Freeze...)
def main_is_frozen(): return (
	hasattr(sys, "frozen") or    # new py2exe
	hasattr(sys, "importers") or # old py2exe
	imp.is_frozen("__main__")    # tools/freeze
)

# configure globals
ROOT = os.path.normpath(os.path.abspath(os.path.dirname(sys.executable if main_is_frozen() else __file__)))
KEYRINGS = os.path.normpath(os.path.join(ROOT, ".keyring"))
PROMPT = "@ %s> " % cfg.__NET__
WALLET = None
try: os.makedirs(KEYRINGS)
except:pass

# redirect logging
logger = logging.getLogger() # get root logger
formatter = logging.Formatter('[%(asctime)s] %(message)s')
file_handler = logging.FileHandler(os.path.normpath(os.path.join(ROOT, "tx.log")), 'a')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)
for handler in logger.handlers[:]:
	logger.removeHandler(handler)
logger.addHandler(file_handler) 

# define commands according docopt lib
commands = {
	"execute":"""
This command execute an arky script file.

Usage: execute <script>
""",

	"connect": """
    This command selects a specific node address to send requests to the
    blockchain. This action is not needed and is used only by developer.

Usage: connect [<peer>]
""",

	"use" : """
    This command selects the network you want to work with. Two networks are
    presently available : ark and testnet. By default, command line interface
    starts on testnet.

Usage: use <network>
""",

	"account": u'''
    This command allows you to perform all kinds of transactions available
    within the ARK blockchain (except for multisignature) and to check some
    information.

    The very first step is to link to an ARK account using link subcommand
    below.

    Example:
    @ mainnet> account link secret
    AJWRd23HNEhPLkK1ymMnwnDBX2a7QBZqff @ mainnet>

    When account is linked, keys are registered locally in .keyring directory as
    an *.akr file according to PEM format. This way secret passphrases are only
    typed once and can not be read from disk.

    You can remove thoses files manually or via unlink or clear subcommand. No
    ARK are stored in *.akr files. Please note that *.akr files gives total
    access to associated an account within arky API.

    With send, split, share and support subcommands, there are three ways to
    define amount:
    1. ARK value (not in SATOSHI) using sinple float
    2. a percentage of the account balance using % symbol (63% will take 63
       percent of wallet balance)
    3. a currency value using \u0024, \u00a3 or \u00a5 symbol (\u002445.6 will be converted in 
       ARK using coinmarketcap API)

Usage: account link [[<secret> [<2ndSecret>]] | [-a <address>] | [-k <keyring>]]
       account save <keyring>
       account clear
       account unlink
       account status
       account balance
       account contributors
       account register <username>
       account register 2ndSecret <secret>
       account vote [-u <delegate>... | -d <delegate>...]
       account send <amount> <address> [<message>]
       account split <amount> <recipient>... [-m <message>]
       account share <amount> [-b <blacklist> -f <floor> -c <ceil> <message>]
       account support <amount> [<message>]

Options:
-u --up                                up vote all delegates name folowing
-d --down                              down vote all delegates name folowing
-b <blacklist> --blacklist <blacklist> comma-separated ark addresse list (no space)
-a <address> --address <address>       already linked ark address
-m <message> --message <message>       64-char message
-k <keyring> --keyring <keyring>       a valid *.akr pathfile
-f <floor> --floor <floor>             minimum treshold ratio to benefit from share
-c <ceil> --ceil <ceil>                maximum share ratio benefit

Subcommands:
    link         : link to account using secret passphrases, Ark address or
                   *.akr file. If secret passphrases contains spaces, it must be
                   enclosed within double quotes ("secret with spaces"). Note
                   that you can use address only for *.akr files registered
                   locally.
    save         : save linked account to an *.akr file.
    clear        : unlink account and delete all *.akr files registered locally.
    unlink       : unlink account and delete its associated *.akr file.
    status       : show information about linked account.
    balance      : show account balance in ARK.
    contributors : show voters contributions ([address - vote weight] pairs).
    register     : register linked account as delegate (cost 25 ARK);
                   or
                   register second signature to linked account (cost 5 ARK).
    vote         : up or/and down vote delegates from linked account.
    send         : send ARK amount to address. You can set a 64-char message.
    split        : equal-split ARK amount to different recipient. You can set a
                   64-char message.
    share        : share ARK amount with voters (if any) according to their
                   weight. You can set a 64-char message.
    support      : share ARK amount to relay nodes according to their vote rate.
                   You can set a 64-char message.
'''
}

def _check(line, num=0):
	global PROMPT
	argv = shlex.split(line.strip())
	print("%s%r" % (PROMPT, argv))
	cmd = argv[0]
	doc = commands.get(cmd, False)
	if doc:
		try:
			arguments = docopt(doc, argv=argv[1:])
			return cmd, arguments
		except:
			input(">>> Syntax error on line %d: %sType <Enter> to close..." % (num, line))
			return False
	else:
		input(">>> Unknown command on line %d: %sType <Enter> to close..." % (num, line))
		return False

def _execute(lines):
	num = 0
	for line in lines:
		num += 1
		if line not in [""]:
			result = _check(line, num)
			if result:
				cmd, arguments = result
				func = COMMANDS.get(cmd, False)
				if func:
					try:
						func(arguments)
					except Exception as error:
						print(error)
						return False
				else:
					print("Not implemented yet")
					return False
			else:
				return False
	return True

# this function is called every 10 s and stops when second secret is set
@setInterval(10)
def _secondSignatureSetter(wlt, passphrase):
	# if second signature is updated in wallet
	if wlt.account.get('secondSignature', False):
		# set second secret
		wlt.secondSecret = passphrase
		# stop setInterval thread
		wlt._stop_2ndSignature_daemon.set()
		delattr(wlt, "_stop_2ndSignature_daemon")
		# update keyring
		WALLET.save(os.path.join(KEYRINGS, WALLET.address+".akr"))
		print("\n    Second signature set for %s\n%s" % (wlt.address, PROMPT), end="")

def _checkWallet(wlt):
	if isinstance(wlt, wallet.Wallet) and wlt.account != {}: return True
	else: print("Account not linked or does not exist in blockchain yet")
	return False

def _prettyPrint(dic, tab="    "):
	if len(dic):
		maxlen = max([len(e) for e in dic.keys()])
		for k,v in dic.items():
			if isinstance(v, dict):
				print(tab + "%s:" % k.ljust(maxlen))
				_prettyPrint(v, tab*2)
			else:
				print(tab + "%s: %s" % (k.ljust(maxlen),v))
	else:
		print("Nothing here")

# get all keyrings registered in KEYRINGS folder
def _getKeyring():
	return [f for f in os.listdir(os.path.join(KEYRINGS, cfg.__NET__)) if f.endswith(".akr")]

# return ark value according to amount
def _floatAmount(amount):
	global WALLET
	if amount.endswith("%"): return float(amount[:-1])/100 * WALLET.balance
	# $10, €10, £10 and ¥10 are converted into ARK using coinmarketcap API
	elif amount.startswith("$"): return float(amount[1:])/getArkPrice("usd")
	elif amount.startswith("€"): return float(amount[1:])/getArkPrice("eur")
	elif amount.startswith("£"): return float(amount[1:])/getArkPrice("gbp")
	elif amount.startswith("¥"): return float(amount[1:])/getArkPrice("cny")
	else: return float(amount)

# 
def _blacklistContributors(contributors, lst):
	share = 0.
	for addr,ratio in [(a,r) for a,r in contributors.items() if a in lst]:
		share += contributors.pop(addr)
	share /= len(contributors)
	for addr,ratio in [(a,r) for a,r in contributors.items()]:
		contributors[addr] += share
	return contributors

def _floorContributors(contributors, min_ratio):
	return _blacklistContributors(contributors, [a for a,r in contributors.items() if r < min_ratio])

def _ceilContributors(contributors, max_ratio):
	nb_cont = len(contributors)
	test = 1./nb_cont
	if test >= max_ratio:
		return dict([(a,test) for a in contributors])
	else:
		share = 0
		nb_cuts = 0
		for addr,ratio in contributors.items():
			diff = ratio - max_ratio
			if diff > 0:
				share += diff
				nb_cuts += 1
				contributors[addr] = max_ratio
		share /= (nb_cont - nb_cuts)
		for addr in [a for a in contributors if contributors[a] <= (max_ratio-share)]:
			contributors[addr] += share
		return contributors

def execute(param):
	if os.path.exists(param["<script>"]):
		with open(param["<script>"]) as src:
			return _execute(src.readlines())
	else:
		print("'%s' script file does not exist" % param["<script>"])
		return False

def connect(param):
	if param["<peer>"]:
		old_url = cfg.__URL_BASE__
		cfg.__URL_BASE__ = "http://" + param["<peer>"]
		test = api.Block.getNethash()
		_prettyPrint(api.Block.getNethash())
		if test == {}: cfg.__URL_BASE__ = old_url
	print("    Actual peer : %s" % cfg.__URL_BASE__)

def use(param):
	global PROMPT, WALLET
	api.use(param["<network>"])
	PROMPT = "@ %s> " % cfg.__NET__
	WALLET = None
	try: os.makedirs(os.path.join(KEYRINGS, cfg.__NET__))
	except:pass

def account(param):
	global PROMPT, WALLET, KEYRINGS

	if param["link"]:
		if param["--keyring"]:
			if os.path.exists(param["--keyring"]):
				WALLET = wallet.open(param["--keyring"])
			else:
				print("Keyring '%s' does not exist" % param["--keyring"])
				return False
		if param["--address"]:
			pathfile = os.path.join(KEYRINGS, cfg.__NET__, param["--address"]+".akr")
			if os.path.exists(pathfile):
				WALLET = wallet.open(pathfile)
			else:
				print("Ark address %s not linked yet" % param["--address"])
				return False
		elif param["<2ndSecret>"]:
			WALLET = wallet.Wallet(param["<secret>"].encode("ascii"), param["<2ndSecret>"].encode("ascii"))
		elif param["<secret>"]:
			WALLET = wallet.Wallet(param["<secret>"].encode("ascii"))
		else:
			names = _getKeyring()
			nb_name = len(names)
			if nb_name > 1:
				for i in range(nb_name):
					print("    %d - %s" % (i+1, names[i]))
				i = 0
				while i < 1 or i > nb_name:
					i = input("Choose a keyring [1-%d]> " % nb_name)
					try: i = int(i)
					except: i = 0
				name = names[i-1]
			elif nb_name == 1:
				name = names[0]
			else:
				print("No account found localy")
				return
			WALLET = wallet.open(os.path.join(KEYRINGS, cfg.__NET__, name))

		pathfile = os.path.join(KEYRINGS, cfg.__NET__, WALLET.address+".akr")
		if not os.path.exists(pathfile): WALLET.save(pathfile)
		PROMPT = "%s @ %s> " % (WALLET.address, cfg.__NET__)

	elif param["clear"]:
		for filename in _getKeyring():
			os.remove(os.path.join(KEYRINGS, filename))
		PROMPT = "@ %s> " % cfg.__NET__
		WALLET = None

	elif param["status"]:
		if _checkWallet(WALLET):
			if WALLET.delegate: _prettyPrint(WALLET.delegate)
			else: _prettyPrint(WALLET.account)

	elif param["balance"]:
		if _checkWallet(WALLET):
			acc = WALLET.account
			_prettyPrint({
				"confirmed": float(acc["balance"])/100000000,
				"unconfirmed": float(acc["unconfirmedBalance"])/100000000
			})

	elif param["register"]:
		if _checkWallet(WALLET):
			if param["2ndSecret"]:
				secondSecret = param["<secret>"].encode("ascii")
				newPublicKey = binascii.hexlify(core.getKeys(secondSecret).public)
				newPublicKey = newPublicKey.decode() if isinstance(newPublicKey, bytes) else newPublicKey
				tx = WALLET._generate_tx(type=1, asset=ArkyDict(signature=ArkyDict(publicKey=newPublicKey)))
				if hasattr(WALLET, "_stop_2ndSignature_daemon"):
					WALLET._stop_2ndSignature_daemon.set()
					delattr(WALLET, "_stop_2ndSignature_daemon")
				WALLET._stop_2ndSignature_daemon = _secondSignatureSetter(WALLET, secondSecret)
			else:
				username = param["<username>"].encode("ascii").decode()
				tx = WALLET._generate_tx(type=2, asset=ArkyDict(delegate=ArkyDict(username=username, publicKey=WALLET.publicKey)))
			_prettyPrint(core.sendTransaction(tx))

	elif param["vote"]:
		if _checkWallet(WALLET):
			votes = WALLET.votes
			if param["--up"]:
				usernames = [c for c in param["<delegate>"] if c not in votes]
				delegates = ["+"+d1['publicKey'] for d1 in [d0 for d0 in wallet.Wallet.delegates if d0['username'] in usernames]]
			elif param["--down"]:
				usernames = [c for c in param["<delegate>"] if c in votes]
				delegates = ["-"+d1['publicKey'] for d1 in [d0 for d0 in wallet.Wallet.delegates if d0['username'] in usernames]]
			try:
				if len(delegates):
					tx = WALLET._generate_tx(type=3, recipientId=WALLET.address, asset=ArkyDict(votes=delegates))
					_prettyPrint(core.sendTransaction(tx))
				else:
					print("Nothing to change on the vote")
			except:
					print("Your curent vote%s: %r" % ("s" if len(votes)>1 else "", votes))

	elif param["contributors"]:
		if _checkWallet(WALLET): 
			_prettyPrint(WALLET.contributors)

	elif param["send"]:
		if _checkWallet(WALLET):
			amount = _floatAmount(param["<amount>"])
			if "%" in param["<amount>"]: amount = amount*100000000 - cfg.__FEES__["send"]
			else: amount *= 100000000
			tx = WALLET._generate_tx(type=0, amount=amount, recipientId=param["<address>"], vendorField=param["<message>"])
			_prettyPrint(core.sendTransaction(tx))

	elif param["share"]:
		if _checkWallet(WALLET):
			contributors = WALLET.contributors
			if param["--blacklist"]:
				contributors = _blacklistContributors(contributors, param["--blacklist"].split(","))
			if param["--floor"]:
				contributors = _floorContributors(contributors, float(param["--floor"])/100)
			if param["--ceil"]:
				contributors = _ceilContributors(contributors, float(param["--ceil"])/100)
			if len(contributors):
				amount = _floatAmount(param["<amount>"])
				for addr,ratio in [(a,r) for a,r in contributors.items() if r > 0.]:
					if "%" in param["<amount>"]: share = amount*ratio*100000000 - cfg.__FEES__["send"]
					else: share = (amount*ratio)*100000000
					tx = WALLET._generate_tx(type=0, amount=share, recipientId=addr, vendorField=param["<message>"])
					_prettyPrint(core.sendTransaction(tx))
			else:
				print("No contributors to share A%.8f with" % _floatAmount(param["<amount>"]))

	elif param["support"]:
		if _checkWallet(WALLET):
			amount = _floatAmount(param["<amount>"])
			relays = api.Delegate.getCandidates()[52:]
			vote_sum = sum([float(d.get("vote", 0.)) for d in relays])
			dist = dict([(r["address"], float(r.get("vote", 0.))/vote_sum) for r in relays])
			for addr,ratio in dist.items():
				share = amount*ratio*100000000 - cfg.__FEES__["send"]
				if share > 100000000.:
					tx = WALLET._generate_tx(type=0, amount=share, recipientId=addr, vendorField=param["<message>"])
					_prettyPrint(core.sendTransaction(tx))

	elif param["split"]:
		if _checkWallet(WALLET):
			share = _floatAmount(param["<amount>"]) / len(param["<recipient>"])
			if "%" in param["<amount>"]: share = share*100000000 - cfg.__FEES__["send"]
			else: share *= 100000000
			for addr in param["<recipient>"]:
				tx = WALLET._generate_tx(type=0, amount=share, recipientId=addr, vendorField=param["--message"])
				_prettyPrint(core.sendTransaction(tx))

	elif param["save"]:
		if _checkWallet(WALLET):
			name = param["<keyring>"]
			if not name.endswith(".akr"):
				name += ".akr"
			WALLET.save(name)

	elif param["unlink"]:
		if _checkWallet(WALLET):
			pathfile = os.path.join(KEYRINGS, WALLET.address+".akr")
			if os.path.exists(pathfile):
				os.remove(pathfile)
			WALLET = None
			PROMPT = "@ %s> " % cfg.__NET__

# create a dictionary with all function defined here
COMMANDS = dict([n,f] for n,f in globals().items() if callable(f) and not n.startswith("_"))

if __name__ == '__main__':
	exit = False
	use({"<network>":"testnet"})

	launch_args = docopt("""
Usage: arky-cli [-s <script>]

Options:
-s <script> --script <script> path to an *.ast file
""")

	if launch_args["--script"]:
		if os.path.exists(launch_args["--script"]):
			with open(launch_args["--script"]) as src:
				error = _execute(src.readlines())
			if not error:
				sys.exit()
		else:
			print("'%s' script file does not exists" % launch_args["--script"])

	print("### Welcome to arky command line interface v%s ###" % __version__)
	while not exit:
		# wait for command line
		try: argv = shlex.split(input(PROMPT).strip())
		except EOFError: exit, argv = True, []
		
		if len(argv):
			cmd = argv[0]

			if argv == ["exit"]:
				exit = True

			else:
				doc = commands.get(cmd, False)
				if doc:
					try:
						arguments = docopt(doc, argv=argv[1:])
						# _prettyPrint(arguments)
					except:
						print(commands.get(cmd))
					else:
						func = COMMANDS.get(cmd, False)
						if func:
							try:
								func(arguments)
							except Exception as error:
								if hasattr(error, "__traceback__"):
									print("".join(traceback.format_tb(error.__traceback__)).rstrip())
								print(error)
						else:
							print("Not implemented yet")
				else:
					print(u"\narky-cli v%s \u00a9 Toons\nHere is a list of command\n" % __version__)
					print("\n".join(["-- %s --%s" % (k,v) for k,v in commands.items()]))
