# -*- encoding: utf8 -*-
# © Toons

__all__ = ["escrow", "network", "delegate", "account"]

from .. import cfg, __PY3__, __version__, main_is_frozen
import os, sys, shlex, docopt, logging, traceback

rootfolder = os.path.normpath(os.path.abspath(os.path.dirname(sys.executable) if main_is_frozen() else __path__[0]))
__path__.append(os.path.normpath(os.path.normpath(os.path.join(rootfolder, "private"))))

from . import escrow, network, delegate, account

__doc__ = """### arky-cli v2.1 - [arky %(version)s embeded]
Available commands: %(sets)s""" % {"version":__version__, "sets": ", ".join(__all__)}

input = raw_input if not __PY3__ else input

def _whereami():
	return ""

class _Prompt(object):

	def __setattr__(self, attr, value):
		object.__setattr__(self, attr, value)

	def __repr__(self):
		return "%(hoc)s@%(net)s/%(wai)s> " % {
			"hoc": "hot" if cfg.__HOT_MODE__ else "cold",
			"net": cfg.__NET__,
			"wai": self.module._whereami()
		}

PROMPT = _Prompt()
PROMPT.module = sys.modules[__name__]

def parse(argv):
	if argv[0] in __all__:
		module = getattr(sys.modules[__name__], argv[0])
		if hasattr(module, "_whereami"):
			PROMPT.module = module
			if len(argv) > 1:
				return parse(argv[1:])
		else:
			PROMPT.module = sys.modules[__name__]
	elif argv[0] in ["exit", ".."]:
		if PROMPT.module == sys.modules[__name__]:
			return False, False
		else:
			PROMPT.module = sys.modules[__name__]
	elif argv[0] in ["help", "?"]:
		sys.stdout.write("%s\n" % PROMPT.module.__doc__.strip())
	elif hasattr(PROMPT.module, argv[0]):
		try:
			arguments = docopt.docopt(PROMPT.module.__doc__, argv=argv)
		except:
			arguments = False
			sys.stdout.write("%s\n" % PROMPT.module.__doc__.strip())
		finally:
			return getattr(PROMPT.module, argv[0]), arguments
	else:
		sys.stdout.write("Command %s does not exist\n" % argv[0])

	return True, False

def start():
	sys.stdout.write(__doc__+"\n")
	exit = False
	while not exit:
		command = input(PROMPT)
		logging.info(command)
		argv = shlex.split(command)
		if len(argv):
			cmd, arg = parse(argv)
			if not cmd:
				exit = True
			elif arg:
				try:
					cmd(arg)
				except Exception as error:
					if hasattr(error, "__traceback__"):
						sys.stdout.write("".join(traceback.format_tb(error.__traceback__)).rstrip() + "\n")
					sys.stdout.write("%s\n" % error)

def execute(*lines):
	pass
