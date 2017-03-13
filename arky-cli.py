# -*- encoding: utf8 -*-
# © Toons

from arky import cfg, api, core, wallet, ArkyDict, __PY3__, setInterval
from docopt import docopt
import os, sys, imp, shlex, traceback, binascii

__DEBUG__ = True if sys.argv[-1] in ["-d", "--debug"] else False
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
	"connect": "Usage: connect (<peer>)",
	"use" : "Usage: use (<network>)\n",
	"account": """
Usage: account open [[<secret> [<2ndSecret>]] | [-a <address>]]
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
-u <list> --up <list>            coma-separated username list to be voted up (no spaces)
-d <list> --down <list>          coma-separated username list to be voted down (no spaces)
-a <address> --account <address> registered ark address
"""
}

@setInterval(10)
def secondSignatureSetter(wlt, passphrase):
	try: wlt.secondSecret = passphrase
	except SecondSignatureError: pass
	else:
		wlt._stop_2ndSignature_daemon.set()
		delattr(wlt, "_stop_2ndSignature_daemon")
		WALLET.save(os.path.join(ROOT, WALLET.address+".awt"))

def checkWallet(wlt):
	if isinstance(wlt, wallet.Wallet) and wlt.account != {}: return True
	else: print("Account not loaded or does not exists in blockchain yet")
	return False

def prettyPrint(dic, tab="    "):
	if len(dic):
		maxlen = max([len(e) for e in dic.keys()])
		for k,v in dic.items():
			if isinstance(v, dict):
				print(tab + "%s:" % k.ljust(maxlen))
				prettyPrint(v, tab*2)
			else:
				print(tab + "%s: %s" % (k.ljust(maxlen),v))
	else:
		print("Nothing here")

def getAccount():
	start = "A" if cfg.__NET__ == "mainnet" else "a"
	return [f for f in os.listdir(ROOT) if f.endswith(".awt") and f.startswith(start)]

def use(param):
	global PROMPT, WALLET
	api.use(param["<network>"])
	PROMPT = "@ %s> " % cfg.__NET__
	WALLET = None

def account(param):
	global PROMPT, WALLET

	if param["open"]:
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
			names = getAccount()
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

	elif param["status"]:
		if checkWallet(WALLET):
			if WALLET.delegate: prettyPrint(WALLET.delegate)
			else: prettyPrint(WALLET.account)

	elif param["balance"]:
		if checkWallet(WALLET):
			acc = WALLET.account
			prettyPrint({
				"confirmed": float(acc["balance"])/100000000,
				"unconfirmed": float(acc["unconfirmedBalance"])/100000000
			})

	elif param["register"]:
		if checkWallet(WALLET):
			if param["2ndSecret"]:
				secondSecret = param["<secret>"].encode("ascii")
				newPublicKey = binascii.hexlify(core.getKeys(secondSecret).public)
				newPublicKey = newPublicKey.decode() if isinstance(newPublicKey, bytes) else newPublicKey
				tx = WALLET._generate_tx(type=1, asset=ArkyDict(signature=ArkyDict(publicKey=newPublicKey)))
				if hasattr(WALLET, "_stop_2ndSignature_daemon"):
					WALLET._stop_2ndSignature_daemon.set()
					delattr(WALLET, "_stop_2ndSignature_daemon")
				WALLET._stop_2ndSignature_daemon = secondSignatureSetter(WALLET, secondSecret)

			else:
				username = param["<username>"].encode("ascii").decode()
				tx = WALLET._generate_tx(type=2, asset=ArkyDict(delegate=ArkyDict(username=username, publicKey=WALLET.publicKey)))
			
			prettyPrint(core.sendTransaction(tx))

	elif param["vote"]:
		if checkWallet(WALLET):
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
				prettyPrint(core.sendTransaction(tx))
			else:
				print(WALLET.votes)

	elif param["contribution"]:
		if checkWallet(WALLET): 
			prettyPrint(WALLET.contribution)

	elif param["send"]:
		tx = WALLET._generate_tx(
			type=0,
			amount=float(param["<amount>"])*100000000,
			recipientId=param["<address>"],
			vendorField=param["<message>"]
		)
		prettyPrint(core.sendTransaction(tx))

	elif param["share"]:
		contribution = WALLET.contribution
		if len(contribution):
			amount = float(param["<amount>"])*100000000
			txs = []
			for addr,ratio in [(a,r) for a,r in contribution.items() if r > 0.]:
				txs.append(WALLET._generate_tx(type=0, amount=amount*ratio, recipientId=addr, vendorField=param["<message>"]))
			for tx in txs:
				prettyPrint(core.sendTransaction(tx))
		else:
			print("No contributors to share A%.8f with" % float(param["<amount>"]))

	elif param["save"]:
		if checkWallet(WALLET):
			name = param["<wallet>"]
			if not name.endswith(".awt"): name += ".awt"
			WALLET.save(name)

	elif param["close"]:
		if WALLET:
			pathfile = os.path.join(ROOT, WALLET.address+".awt")
			if os.path.exists(pathfile):
				os.remove(pathfile)
			PROMPT = "@ %s> " % cfg.__NET__

	elif param["clear"]:
		for filename in getAccount():
			os.remove(os.path.join(ROOT, filename))
			PROMPT = "@ %s> " % cfg.__NET__

# create a dictionary with all function defined here
COMMANDS = dict([n,f] for n,f in globals().items() if callable(f))

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
								if hasattr(error, "__traceback__") and __DEBUG__:
									print("".join(traceback.format_tb(error.__traceback__)).rstrip())
								print(error)
						else:
							print("Not implemented yet")
				else:
					print("\narky-cli © Toons\nHere is a list of command\n")
					print("\n".join(["-- %s --\n%s\n" % (k,v.strip()) for k,v in commands.items()]))
