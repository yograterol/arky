# -*- encoding:utf-8 -*-
from arky import wallet, setInterval
import random, threading

choose = lambda obj: obj[int(random.random()*len(obj))%len(obj)]
tx_range = 5

wallet.core.use("ark")
unlock = threading.Event()
wlt = wallet.open("arky.awt")

def loop():
	addresses = [d["address"] for d in wallet.Wallet.delegates if d["address"] != wlt.address]
	while not unlock.isSet():
		amount = random.random()*tx_range
		address = choose(addresses)
		wlt.sendArk(amount, address, vendorField="arky API stress test: deadwhile")

@setInterval(10)
def checkAccount(obj, evt):
	print(obj.balance, "remaining in", obj.address)
	if obj.balance <= 1000:
		evt.set()

checkAccount(wlt, unlock)
t = threading.Thread(target=loop)
t.start()
