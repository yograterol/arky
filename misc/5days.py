# -*- encoding:utf-8 -*-
from arky import wallet, core, api, cfg, setInterval
import time, random, threading

choose = lambda obj: obj[int(random.random()*len(obj))%len(obj)]
tx_range = 1/100.

cfg.__NB_THREADS__ = 12
wallet.mgmt.stop()
# wallet.mgmt.start()

wallet.api.use("ark")
unlock = threading.Event()
wlt = wallet.Wallet("secret")

def loop():
	addresses = [d["address"] for d in wallet.Wallet.delegates if d["address"] != wlt.address]
	bunch = 11000
	wiped = 0
	n = 0
	while not unlock.isSet():
		amount = max(0.0001, random.random()*tx_range)
		address = choose(addresses)
		core.sendTransaction(wlt._generate_tx(amount*100000000, address, vendorField="arky 5 day stress test"))
		n += 1
		wiped += amount
		if wiped > bunch:
			unlock.set()
		time.sleep(0.2) # => 5tx/sec
		
	print("loop exited ! %s transaction sent" % n)

t = threading.Thread(target=loop)
t.start()
unlock.wait()
