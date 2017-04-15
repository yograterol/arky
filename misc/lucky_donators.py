# -*- encoding: utf-8 -*-
from arky.util import getArkPrice
from arky import cfg, api, wallet, HOME
import os, json, math, datetime, random

import sys

api.use("ark")

# screen command line
from optparse import OptionParser
parser = OptionParser()
parser.set_usage("usage: %prog arg1 ....argN [options]")
parser.add_option("-s", "--secret", dest="secret", help="wallet secret you want to use")
parser.add_option("-2nds", "--second-secret", dest="secondSecret", help="wallet secret you want to use")
parser.add_option("-k", "--keyring", dest="keyring", help="wallet file you want to use")
(options, args) = parser.parse_args()

if len(args) == 1 and os.path.exists(args[0]):
	in_ = open(args[0])
	content = in_.read()
	in_.close()
	conf = json.loads(content.decode() if isinstance(content, bytes) else content)
	wlt = wallet.Wallet(conf["forging"]["secret"][0])
elif options.secret:
	wlt = wallet.Wallet(options.secret, options.secondSecret)
elif options.keyring:
	wlt = wallet.open(options.keyring)
else:
	raise Exception("Can not do something for now !")

logfile = os.path.join(HOME, "Lucky", "%s.pay" % datetime.datetime.now().strftime("%y-%m-%d"))
try: os.makedirs(os.path.dirname(logfile))
except: pass

log = open(logfile, "w")
header = ["Date", datetime.datetime.now(), ""]
content = ["ARK amount", amount, ""]

wlt.update()
now = datetime.datetime.now(slots.UTC)
limit = datetime.datetime(now.year, now.month, now.day-7, 0, 0, tzinfo=slots.UTC)
timestamp_limit = slots.getTime(limit)

tx = api.Transaction.getTransactionsList(recipientId=wlt.address, limit=20).get("transactions", [])
if len(tx):
	# get all tx received after timestamp limit
	if tx[0]["timestamp"] > timestamp_limit:
		while tx[0]["timestamp"] > timestamp_limit:
			tx = api.Transaction.getTransactionsList(recipientId=wlt.address, limit=20, offset=len(tx)).get("transactions", []) + tx
	# last filter
	tx = [t for t in tx if t["timestamp"] >= timestamp_limit and t["amount"] > 90000000]
	
	# select lucky one
	index = int(radom.random()*len(tx))
	recipientId = tx[index]["senderId"]

	# determine total ark given since timestamp_limit
	total_received = sum([t["amount"] for t in tx])
	if recipientId in wlt.contributors:
		share = .2*total_received
	else:
		share = .1*total_received

	summary = {}
	for t in tx:
		senderId = t["senderId"]
		if senderId in summary: summary[senderId] += t["amount"]
		else: summary[senderId] = t["amount"]

	header +=  ["donator number", "Total ARK",               ""]
	content += [len(summary),     total_received/100000000., ""]
	if share >= summary[recipientId]:
		wlt.sendArk(share/100000000., recipientId, vendorField="from arky delegate: You are the lucky donator of the week !")
		header +=  ["Lucky one", "Received", "Ratio"]
		content += [recipientId, share, (share/summary[recipientId]-1)*100]
	else:
		header +=  ["Lucky one"]
		content += ["None"]
		for recipientId, share in summary.items():
			log.write("No lucky donator found this week\n")
			wlt.sendArk(share/100000000., recipientId, vendorField="from arky delegate: No lucky donator found this week")

out = open("lucky.csv", "a")
out.write(";".join(["%s"%e for e in header])  + "\n")
out.write(";".join(["%s"%e for e in content]) + "\n")
out.close()

wallet.mgmt.join()
log.close()
