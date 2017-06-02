# -*- encoding: utf8 -*-
# © Toons

# put cli module name here
__all__ = ["escrow"]

from .. import cfg
from . import escrow
import os, sys, shlex, docopt, traceback


def _whereami():
	return "root"

class _Prompt(object):

	def __setattr__(self, attr, value):
		object.__setattr__(self, attr, value)

	def __repr__(self):
		return "%(hoc)s-%(net)s@%(wai)s> " % {
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
	elif argv[0] == "exit":
		if PROMPT.module == sys.modules[__name__]:
			return False, False
		else:
			PROMPT.module = sys.modules[__name__]
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
	exit = False
	while not exit:
		argv = shlex.split(input(PROMPT))
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
			# else:
			# 	sys.stdout.write("\n".join(getattr(sys.modules[__name__], name).__doc__ for name in __all__))

def execute(*lines):
	pass

# def _blacklistContributors(contributors, lst):
# 	return dict([a,v] for a,v in contributors.items() if a not in lst)

# def _floorContributors(contributors, min_ratio):
# 	total_vote = sum(contributors.values())
# 	cut_vote = min_ratio*total_vote
# 	return _blacklistContributors(contributors, [a for a,v in contributors.items() if v < cut_vote])

# def _ceilContributors(contributors, max_ratio):
# 	total_vote = sum(contributors.values())
# 	cut_vote = max_ratio*total_vote
# 	return dict([a,cut_vote if v/total_vote > max_ratio else v] for a,v in contributors.items())
