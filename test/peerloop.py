# -*- encoding:utf-8 -*-
from arky import wallet, cfg, api, setInterval
import random, threading

choose = lambda obj: obj[int(random.random()*len(obj))%len(obj)]
tx_range = 5

wallet.core.use("ark")

unlock = threading.Event()
wlt = wallet.open("account.awt")
wlt._stop_check_daemon.set()

@setInterval(1)
def launch():
	try: peer = choose(api.Peer.getPeersList().get("peers", []))
	except: peer = {}
	if "string" in peer:
		old_one = cfg.__URL_BASE__
		cfg.__URL_BASE__ = "http://" + peer["string"]
		try: success = api.Loader.getLoadingStatus().get("success", False)
		except: success = False
		if success: cfg.__LOG__.put({"API info": "using peer %s" % cfg.__URL_BASE__})
		else: cfg.__URL_BASE__ = old_one

def loop():
	addresses = [d["address"] for d in wallet.Wallet.delegates if d["address"] != wlt.address]
	bunch = 3000
	wiped = 0
	n = 0
	while not unlock.isSet():
		amount = random.random()*tx_range
		address = choose(addresses)
		wlt.sendArk(amount, address, vendorField="arky API stress test: peerloop")
		n += 1
		wiped += amount
		if wiped > bunch:
			print(wiped, "ARK wipped out ; wallet balance =", wlt.balance)
			unlock.set()
	print("loop exited !", n, "transaction sent")

launch()
t = threading.Thread(target=loop)
t.start()

unlock.clear()
unlock.wait()
