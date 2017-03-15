# -*- encoding: utf8 -*-
# © Toons

from arky import cfg, api, core, wallet, ArkyDict, __PY3__, setInterval
from docopt import docopt
import os, sys, imp, shlex, traceback, binascii

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
	".wallet")
)

PROMPT = "@ %s> " % cfg.__NET__
WALLET = None

try: os.makedirs(ROOT)
except:pass

commands = {
	"execute":"""
This command execute an arky script file.

Usage : execute (<file>)
""",

	"connect": """
This command select a specific node address to send requests to the blockchain.
This action is not needed and is used only by developper.

Usage: connect [<peer>]
""",

	"use" : """
This command select the network you want to work with. Two networks are
presently available : ark and testnet. by default, command line interface
starts on testnet.

Usage: use (<network>)
""",

	"account": '''
This command allows you to perform all kind of transactions available within ARK
blockchain (except multisignature) and to check some informations.

The very first action to do is to link to an ARK account using link subcommand.

Example:
@ mainnet> account link secret
AJWRd23HNEhPLkK1ymMnwnDBX2a7QBZqff @ mainnet>

When account is linked, keys are registers localy in .wallet directory as an
*.awt file according to PEM format. This way secrets are only typed once and can
not be read from disk.

You can remove thoses files manualy or via close or clear subcommand. No ARK are
stored in *.awt files. Note that *.awt files gives total access to associated
account within arky API.

With send and share subcommands, ratio can be used instead of float value. 63%
of total balance can be easily set by 63:100.

Usage: account link [[<secret> [<2ndSecret>]] | [-a <address>]  | [-w <wallet>]]
       account save (<wallet>)
       account clear
       account close
       account status
       account balance
       account contributors
       account register (<username>)
       account register 2ndSecret (<secret>)
       account vote [-u <list>] [-d <list>]
       account send (<amount> <address>) [<message>]
       account share (<amount>) [<message>]

Options:
-u <list> --up <list>            coma-separated username list with no spaces
-d <list> --down <list>          coma-separated username list with no spaces
-a <address> --account <address> registered ark address
-w <wallet> --wallet <wallet>    a valid *.awt pathfile

Subcommands:
 - link         : link to account using secrets, Ark address or *.awt file. If
                  secrets contains spaces, it must be enclosed by double quotes
                  ("secret with spaces"). Note that you can use address only if
                  you already have some *.awt files registered localy.
 - save         : save linked account to an *.awt file.
 - clear        : unlink account and delete all *.awt files registered localy.
 - close        : unlink account and delete its associated *.awt file.
 - status       : show informations about linked account.
 - balance      : show account balance in ARK.
 - contributors : show voters contributions ([address - vote weight] pairs).
 - register     : register linked account as delegate (cost 25 ARK);
                  or
                  register second signature to linked account (cost 5 ARK).
 - vote         : up or/and down vote delegates from linked account.
 - send         : send ARK amount to address. You can set a 64-char message.
 - share        : share ARK amount to voters if any according to their weight.
                  You can set a 64-char message.
'''
}

def _execute(line):
	argv = [l for l in line.split(" ") if l != ""]
	cmd = argv[0]
	doc = commands.get(cmd, False)
	if doc:
		try:
			arguments = docopt(doc, argv=argv[1:])
		except:
			print("bad command '%s'" % line)
			return False
		else:
			func = COMMANDS.get(cmd, False)
			if func:
				try:
					func(arguments)
					return True
				except Exception as error:
					print(error)
					return False
			else:
				print("Not implemented yet")
				return False
	else:
		print("bad command '%s'" % line)
		return False

@setInterval(10)
def _secondSignatureSetter(wlt, passphrase):
	if wlt.account.get('secondSignature', False):
		wlt.secondSecret = passphrase
		wlt._stop_2ndSignature_daemon.set()
		delattr(wlt, "_stop_2ndSignature_daemon")
		WALLET.save(os.path.join(ROOT, WALLET.address+".awt"))
		print("    Second signature set for %s" % self)

def _checkWallet(wlt):
	if isinstance(wlt, wallet.Wallet) and wlt.account != {}: return True
	else: print("Account not loaded or does not exists in blockchain yet")
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
	return [f for f in os.listdir(ROOT) if f.endswith(".awt") and f.startswith(start)]

def _getAmmount(amount):
	if ":" in amount:
		n, d = (float(e) for e in amount.split(":"))
		return WALLET.balance * n/d
	else:
		return float(amount)

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
		if param["--wallet"]:
			WALLET = wallet.open(param["--wallet"])
		if param["--account"]:
			pathfile = os.path.join(ROOT, param["--account"]+".awt")
			if os.path.exists(pathfile):
				WALLET = wallet.open(pathfile)
			else:
				print("Ark address %s not registered yet" % param["--address"])
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
					i = input("Choose a wallet [1-%d]> " % nb_name)
					try: i = int(i)
					except: i = 0
				name = names[i-1]
			elif nb_name == 1:
				name = names[0]
			else:
				print("No account found localy")
				return
			WALLET = wallet.open(os.path.join(ROOT, name))

		pathfile = os.path.join(ROOT, WALLET.address+".awt")
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
			tx = WALLET._generate_tx(
				type=0,
				amount=_getAmmount(param["<amount>"])*100000000,
				recipientId=param["<address>"],
				vendorField=param["<message>"]
			)
			_prettyPrint(core.sendTransaction(tx))

	elif param["share"]:
		if _checkWallet(WALLET):
			contributors = WALLET.contributors
			if len(contributors):
				share = _getAmmount(param["<amount>"])*100000000
				for addr,ratio in [(a,r) for a,r in contributors.items() if r > 0.]:
					tx = WALLET._generate_tx(type=0, amount=share*ratio, recipientId=addr, vendorField=param["<message>"])
					_prettyPrint(core.sendTransaction(tx))
			else:
				print("No contributors to share A%.8f with" % _getAmmount(param["<amount>"]))

	elif param["save"]:
		if _checkWallet(WALLET):
			name = param["<wallet>"]
			if not name.endswith(".awt"):
				name += ".awt"
			WALLET.save(name)

	elif param["close"]:
		if _checkWallet(WALLET):
			pathfile = os.path.join(ROOT, WALLET.address+".awt")
			if os.path.exists(pathfile):
				os.remove(pathfile)
			WALLET = None
			PROMPT = "@ %s> " % cfg.__NET__

# create a dictionary with all function defined here
COMMANDS = dict([n,f] for n,f in globals().items() if callable(f) and not n.startswith("_"))

if __name__ == '__main__':
	exit = False

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
						print("\n"+commands.get(cmd).strip()+"\n")
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
					print("\narky-cli © Toons\nHere is a list of command\n")
					print("\n".join(["-- %s --\n%s\n" % (k,v.strip()) for k,v in commands.items()]))
