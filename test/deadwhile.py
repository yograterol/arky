# -*- encoding:utf-8 -*-
from arky import wallet, api, setInterval
import random, threading

choose = lambda obj: obj[int(random.random()*len(obj))%len(obj)]
tx_range = 5

wallet.core.use("ark")
unlock = threading.Event()
wlt = wallet.open("account.awt")

def loop():
	addresses = [d["address"] for d in wallet.Wallet.delegates if d["address"] != wlt.address]
	bunch = 3000
	wiped = 0
	n = 0
	while not unlock.isSet():
		amount = random.random()*tx_range
		address = choose(addresses)
		wlt.sendArk(amount, address, vendorField="arky API stress test: deadwhile")
		n += 1
		wiped += amount
		if wiped > bunch:
			print(wiped, "ARK wipped out ; wallet balance =", wlt.balance)
			unlock.set()
	print("loop exited !", n, "transaction sent")

t = threading.Thread(target=loop)
t.start()
