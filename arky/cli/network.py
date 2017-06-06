# -*- encoding: utf8 -*-
# © Toons

'''
Usage: network use <name> [-b <number> -s <seed> -l <ms>]
       network address <secret>
       network delegates
       network ping

Options:
-b <number> --broadcast <number> peer number to use for broadcast      [default: 10]
-s <seed> --custom-seed <seed>   custom seed you want to connect with
-l <ms> --latency <ms>           maxium latency allowed in miliseconds [default: 1000]

Subcommands:
    use       : ...
    address   : ...
    delegates : ...
    ping      : ...
'''

from .. import api, core
from . import common
import sys

def _whereami():
	return "network"

def use(param):
	api.use(
		param.get("<name>"),
		custom_seed=param.get("--custom-seed"),
		broadcast=int(param.get("--broadcast")),
		latency=float(param.get("--latency"))/1000
	)

def ping(param):
	common.prettyPrint(dict([peer,api.checkPeerLatency(peer)] for peer in api.PEERS))

def address(param):
	common.prettyPrint({param["<secret>"]:core.getAddress(core.getKeys(param["<secret>"]))})

def delegates(param):
	delegates = api.Delegate.getDelegates(limit=51, returnKey='delegates')
	maxlen = max([len(d["username"]) for d in delegates])
	for name, vote in sorted([(d["username"],float(d["vote"])/100000000) for d in delegates], key=lambda e:e[-1], reverse=True):
		sys.stdout.write("    %s: %.3f\n" % (name.ljust(maxlen), vote))
