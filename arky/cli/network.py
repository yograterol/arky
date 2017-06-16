# -*- encoding: utf8 -*-
# © Toons

'''
Usage: network use [<name> -b <number> -s <seed> -l <ms>]
       network publickey <secret>
       network address <secret>
       network wif <secret>
       network delegates
       network ping

Options:
-b <number> --broadcast <number> peer number to use for broadcast       [default: 10]
-s <seed> --custom-seed <seed>   custom seed you want to connect with
-l <ms> --latency <ms>           maximum latency allowed in miliseconds [default: 1000]

Subcommands:
    use       : select network.
    publickey : returns public key from secret.
    address   : returns address from secret.
    delegates : show delegate list.
    ping      : print selected peer latency.
'''

from .. import cfg, api, core
from . import common

import sys, hashlib

def _whereami():
	return "network"

def use(param):
	if not param["<name>"]:
		choices = common.findNetworks()
		if choices:
			param["<name>"] = common.chooseItem("Network(s) found:", *choices)
		else:
			sys.stdout.write("No Network found\n")
			return False
	api.use(
		param.get("<name>"),
		custom_seed=param.get("--custom-seed"),
		broadcast=int(param.get("--broadcast")),
		latency=float(param.get("--latency"))/1000
	)

def ping(param):
	common.prettyPrint(dict(
		[[">>> "+cfg.__URL_BASE__,api.checkPeerLatency(cfg.__URL_BASE__)]]+\
		[[peer,api.checkPeerLatency(peer)] for peer in api.PEERS]
	))

#       network details <secret>
# def details(param):
# 	secret = param["<secret>"].encode("ascii")
# 	common.prettyPrint({
# 		"address": core.getAddress(core.getKeys(secret)),
# 		"public key": common.hexlify(core.getKeys(secret).public),
# 		"wif": core.getWIF(hashlib.sha256(secret).digest(), cfg.__NETWORK__)
# 	})

def address(param):
	sys.stdout.write("    %s\n" % core.getAddress(core.getKeys(param["<secret>"].encode("ascii"))))

def publickey(param):
	sys.stdout.write("    %s\n" % common.hexlify(core.getKeys(param["<secret>"].encode("ascii")).public))

def wif(param):
	sys.stdout.write("    %s\n" % core.getWIF(hashlib.sha256(param["<secret>"].encode("ascii")).digest(), cfg.__NETWORK__))

def delegates(param):
	delegates = api.Delegate.getDelegates(limit=51, returnKey='delegates')
	maxlen = max([len(d["username"]) for d in delegates])
	for name, vote in sorted([(d["username"],float(d["vote"])/100000000) for d in delegates], key=lambda e:e[-1], reverse=True):
		sys.stdout.write("    %s: %.3f\n" % (name.ljust(maxlen), vote))
