# -*- encoding: utf8 -*-
# © Toons

from arky import cfg, api, core, wallet, ArkyDict, __PY3__, setInterval
from arky.util import getArkPrice
from docopt import docopt
import os, sys, imp, shlex, traceback, binascii

__version__ = "1.0"

input = raw_input if not __PY3__ else input 

# return True if it runs from a frozen script (py2exe, cx_Freeze...)
def main_is_frozen(): return (
	hasattr(sys, "frozen") or    # new py2exe
	hasattr(sys, "importers") or # old py2exe
	imp.is_frozen("__main__")    # tools/freeze
)

# path setup on package import
ROOT = os.path.normpath(os.path.join(
	os.path.abspath(os.path.dirname(sys.executable) if main_is_frozen() else os.path.dirname(__file__)),
	".keyring")
)

PROMPT = "@ %s> " % cfg.__NET__
WALLET = None

try: os.makedirs(ROOT)
except:pass

commands = {
	"execute":"""
This command execute an arky script file.

Usage: execute (<script>)
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

Usage: use (<network>)
""",

	"account": '''
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

    With send and share subcommands, there are three ways to define amount:
    1. ARK value (not in SATOSHI) using sinple float
    2. a percentage of the account balance using semicolon marker (63:100 = 63%,
       1:4 = 25%)
    3. a currency value using $, £, € or ¥ symbol ($45.6 will be converted in 
       ARK using coinmarketcap API)

Usage: account link [[<secret> [<2ndSecret>]] | [-a <address>] | [-k <keyring>]]
       account save (<keyring>)
       account clear
       account unlink
       account status
       account balance
       account contributors
       account register (<username>)
       account register 2ndSecret (<secret>)
       account vote [-u <list>] [-d <list>]
       account send (<amount> <address>) [<message>]
       account share (<amount>) [-b <blacklist> -f <floor> -c <ceil> <message>]
       account support (<amount>) [<message>]

Options:
-u <list> --up <list>                  comma-separated username list (no space)
-d <list> --down <list>                comma-separated username list (no space)
-b <blacklist> --blacklist <blacklist> comma-separated ark addresse list (no space)
-a <address> --address <address>       already linked ark address
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

@setInterval(10)
def _secondSignatureSetter(wlt, passphrase):
	if wlt.account.get('secondSignature', False):
		wlt.secondSecret = passphrase
		wlt._stop_2ndSignature_daemon.set()
		delattr(wlt, "_stop_2ndSignature_daemon")
		WALLET.save(os.path.join(ROOT, WALLET.address+".akr"))
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

def _getAccount():
	start = "A" if cfg.__NET__ == "mainnet" else "a"
	return [f for f in os.listdir(ROOT) if f.endswith(".akr") and f.startswith(start)]

def _float(amount, what=1.0):
	if ":" in amount:
		n, d = (float(e) for e in amount.split(":"))
		return n/d * what
	elif amount.startswith("$"): return float(amount[1:])/getArkPrice("usd")
	elif amount.startswith("€"): return float(amount[1:])/getArkPrice("eur")
	elif amount.startswith("£"): return float(amount[1:])/getArkPrice("gbp")
	elif amount.startswith("¥"): return float(amount[1:])/getArkPrice("cny")
	else: return float(amount)

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

def account(param):
	global PROMPT, WALLET

	if param["link"]:
		if param["--keyring"]:
			if os.path.exists(param["--keyring"]):
				WALLET = wallet.open(param["--keyring"])
			else:
				print("Keyring '%s' does not exist" % param["--keyring"])
				return False
		if param["--address"]:
			pathfile = os.path.join(ROOT, param["--address"]+".akr")
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
			names = _getAccount()
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
			WALLET = wallet.open(os.path.join(ROOT, name))

		pathfile = os.path.join(ROOT, WALLET.address+".akr")
		if not os.path.exists(pathfile): WALLET.save(pathfile)
		PROMPT = "%s @ %s> " % (WALLET.address, cfg.__NET__)

	elif param["clear"]:
		for filename in _getAccount():
			os.remove(os.path.join(ROOT, filename))
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
			up = param["--up"]
			down = param["--down"]
			# first filter
			up = [u for u in up.split(",") if u not in votes and u in wallet.Wallet.candidates] if up else []
			down = [u for u in down.split(",") if u in votes] if down else []
			#second filter
			up = [d1['publicKey'] for d1 in [d0 for d0 in wallet.Wallet.delegates if d0['username'] in up]]
			down = [d1['publicKey'] for d1 in [d0 for d0 in wallet.Wallet.delegates if d0['username'] in down]]
			# concatenate votes
			usernames = ['+'+c for c in up] + ['-'+c for c in down]
			# send votes
			if len(usernames):
				tx = WALLET._generate_tx(type=3, recipientId=WALLET.address, asset=ArkyDict(votes=usernames))
				_prettyPrint(core.sendTransaction(tx))
			else:
				print(WALLET.votes)

	elif param["contributors"]:
		if _checkWallet(WALLET): 
			_prettyPrint(WALLET.contributors)

	elif param["send"]:
		if _checkWallet(WALLET):
			amount = _float(param["<amount>"], WALLET.balance)
			if ":" in param["<amount>"]:
				amount = (amount-0.1)*100000000
			else:
				amount *= 100000000
			tx = WALLET._generate_tx(
				type=0,
				amount=amount,
				recipientId=param["<address>"],
				vendorField=param["<message>"]
			)
			_prettyPrint(core.sendTransaction(tx))

	elif param["share"]:
		if _checkWallet(WALLET):
			contributors = WALLET.contributors
			if param["--blacklist"]:
				contributors = _blacklistContributors(contributors, param["--blacklist"].split(","))
			if param["--floor"]:
				contributors = _floorContributors(contributors, _float(param["--floor"]))
			if param["--ceil"]:
				contributors = _ceilContributors(contributors, _float(param["--ceil"]))
			if len(contributors):
				amount = _float(param["<amount>"], WALLET.balance)
				for addr,ratio in [(a,r) for a,r in contributors.items() if r > 0.]:
					if ":" in param["<amount>"]:
						share = (amount*ratio - 0.1)*100000000
					else:
						share = (amount*ratio)*100000000
					tx = WALLET._generate_tx(type=0, amount=share, recipientId=addr, vendorField=param["<message>"])
					_prettyPrint(core.sendTransaction(tx))
			else:
				print("No contributors to share A%.8f with" % _float(param["<amount>"], WALLET.balance))

	elif param["support"]:
		if _checkWallet(WALLET):
			amount = _float(param["<amount>"], WALLET.balance)
			relays = api.Delegate.getCandidates()[52:]
			vote_sum = sum([float(d.get("vote", 0.)) for d in relays])
			dist = dict([(r["address"], float(r.get("vote", 0.))/vote_sum) for r in relays])
			for addr,ratio in dist.items():
				share = (amount*ratio - 0.1)*100000000
				if share > 1.0:
					tx = WALLET._generate_tx(type=0, amount=share, recipientId=addr, vendorField=param["<message>"])
					_prettyPrint(core.sendTransaction(tx))

	elif param["save"]:
		if _checkWallet(WALLET):
			name = param["<keyring>"]
			if not name.endswith(".akr"):
				name += ".akr"
			WALLET.save(name)

	elif param["unlink"]:
		if _checkWallet(WALLET):
			pathfile = os.path.join(ROOT, WALLET.address+".akr")
			if os.path.exists(pathfile):
				os.remove(pathfile)
			WALLET = None
			PROMPT = "@ %s> " % cfg.__NET__

# create a dictionary with all function defined here
COMMANDS = dict([n,f] for n,f in globals().items() if callable(f) and not n.startswith("_"))

if __name__ == '__main__':
	exit = False

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
					print("\narky-cli v%s © Toons\nHere is a list of command\n" % __version__)
					print("\n".join(["-- %s --%s" % (k,v) for k,v in commands.items()]))
