# -*- encoding:utf-8 -*-
from arky import wallet, cfg, api, setInterval
import random, threading

choose = lambda obj: obj[int(random.random()*len(obj))%len(obj)]
tx_range = 5

wallet.core.use("ark")
unlock = threading.Event()
wlt = wallet.open("account.awt")
treshold = wlt.balance - 2000

wallet.core._stop_rotatePeer_daemon.set()
@setInterval(1)
def launch():
	peers = api.Peer.getPeersList().get("peers", [])
	if len(peers):
		old_one = cfg.__URL_BASE__
		p = choose(peers)
		cfg.__URL_BASE__ = "http://" + p.get("string", "")
		if not api.Loader.getLoadingStatus().get("success", False):
			cfg.__URL_BASE__ = old_one
		cfg.__LOG__.put({"API info": "using peer %s" % cfg.__URL_BASE__})

def loop():
	addresses = [d["address"] for d in wallet.Wallet.delegates if d["address"] != wlt.address]
	while not unlock.isSet():
		amount = random.random()*tx_range
		address = choose(addresses)
		wlt.sendArk(amount, address, vendorField="arky API stress test: peerloop")
		if float(api.Account.getBalance(wlt.address).get("balance", 0)) <= treshold:
			unlock.set()

launch()
t = threading.Thread(target=loop)
t.start()
