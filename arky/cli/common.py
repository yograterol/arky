# -*- encoding: utf8 -*-
# © Toons

from .. import __PY3__, core, cfg
import os, sys, json, logging

input = raw_input if not __PY3__ else input

def prettyfy(dic, tab="    "):
	result = ""
	if len(dic):
		maxlen = max([len(e) for e in dic.keys()])
		for k,v in dic.items():
			if isinstance(v, dict):
				result += tab + "%s:" % k.ljust(maxlen)
				result += prettyfy(v, tab*2)
			else:
				result += tab + "%s: %s" % (k.ljust(maxlen),v)
			result += "\n"
		return result

def prettyPrint(dic, tab="    ", log=True):
	pretty = prettyfy(dic, tab)
	if len(dic):
		sys.stdout.write(pretty)
		if log: logging.info(pretty.strip())
	else:
		sys.stdout.write("Nothing to print here\n")
		if log: logging.info("Nothing to log here")

# return ark value according to amount
def floatAmount(amount, address):
	global EXCHANGE

	if amount.endswith("%"):
		return float(amount[:-1])/100 * float(api.Account.getBalance(address, returnKey="balance"))
	elif amount[0] in "$€£¥":
		price = util.getArkPrice({"$":"usd", "€":"eur", "£":"gbp", "¥":"cny"}[amount[0]])
		result = float(amount[1:])/price
		sys.stdout.write("%s price : ARK/%s = %f -> " % (EXCHANGE, amount[0], price))
		answer = ""
		while answer not in ["y", "Y", "n", "N"]:
			answer = input("%s = ARK%f. Validate? [y-n]> " % (amount, result))
		if answer in ["n", "N"]:
			sys.stdout.write("Transaction aborted\n")
			return False
		return result
	else:
		return float(amount)

def chooseItem(msg, *elem):
	n = len(elem)
	if n > 1:
		sys.stdout.write(msg + "\n")
		for i in range(n):
			sys.stdout.write("    %d - %s\n" % (i+1, elem[i]))
		i = 0
		while i < 1 or i > n:
			i = input("Choose an item: [1-%d]> " % n)
			try: i = int(i)
			except: i = 0
		return elem[i-1]
	elif n == 1:
		return elem[0]
	else:
		sys.stdout.write("Nothing to choose...\n")
		return False

def postData(url_base, data):
	return json.loads(
		core.api.requests.post(
			url_base + "/peer/transactions",
			data=data,
			headers=cfg.__HEADERS__,
			timeout=3
		).text
	)

def broadcastSerial(serial):
	data = json.dumps({"transactions": [serial]})
	result = postData(cfg.__URL_BASE__, data)
	ratio = 0.
	if result["success"]:
		for peer in core.api.PEERS:
			if postData(peer, data)["success"]: ratio += 1
	result["broadcast"] = "%.1f%%" % (ratio/len(core.api.PEERS)*100)
	return result
