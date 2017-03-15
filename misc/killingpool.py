# -*- encoding:utf-8 -*-
from arky import wallet, core, api, cfg, setInterval
import json, random, threading, requests, traceback

choose = lambda obj: obj[int(random.random()*len(obj))%len(obj)]
tx_range = 5
nb_range = 2

cfg.__NB_THREADS__ = 12
wallet.mgmt.stop()
wallet.mgmt.start()

wallet.api.use("ark")
wlt = wallet.open("account.awt") #("secret")
peers = ["%(ip)s:%(port)s" % p for p in api.Peer.getPeersList().get("peers", [])]
addresses = [d["address"] for d in wallet.Wallet.delegates if d["address"] != wlt.address]

def loop():
	bunch = 2500
	wiped = 0
	n = 0
	while wiped < bunch:
		number = max(1, int(random.random()*nb_range))
		transactions = []
		for i in range(number):
			amount = random.random()*tx_range
			address = choose(addresses)
			tx = wlt._generate_tx(amount=amount*100000000, recipientId=address, vendorField="arky API stress test: killingpool")
			tx.sign()
			transactions.append(tx.serialize())
			wiped += amount
		n += 1
		wallet.mgmt.FIFO.put(["http://"+choose(peers)+"/peer/transactions" , json.dumps({"transactions": transactions})])
		if wiped > bunch:
			print(wiped, "ARK wipped out ; wallet balance =", wlt.balance)
	print("loop exited !", n, "transaction sent")

t = threading.Thread(target=loop)
t.start()

wallet.mgmt.join()
