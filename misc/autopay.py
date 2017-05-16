# -*- encoding: utf-8 -*-
from arky.util import getArkPrice
from arky import cfg, api, slots, wallet, HOME
import os, json, math, datetime

import sys
print(sys.version)

while cfg.__NET__ != "mainnet":
	api.use("ark")

__daily_fees__ =  5./30 # daily server cost
__pythoners__ =   "AGvTiwbXykX6zpDMYUEBd9E5J818YmPZ4H"
__investments__ = "AUahWfkfr5J4tYakugRbfow7RWVTK35GPW"
__exchange__ =    "APREAB1cyRLGRrTBs97BEXNv1AwAPpSQkJ"
__tx_fee__ = cfg.__FEES__["send"]/100000000.

# screen command line
from optparse import OptionParser
parser = OptionParser()
parser.set_usage("usage: %prog arg1 ....argN [options]")
parser.add_option("-s", "--secret", dest="secret", help="wallet secret you want to use")
parser.add_option("-k", "--keyring", dest="keyring", help="wallet file you want to use")
(options, args) = parser.parse_args()

def ARK2USD(value): return value * getArkPrice("usd")
def USD2ARK(value): return value / getArkPrice("usd")

if len(args) == 1 and os.path.exists(args[0]):
	in_ = open(args[0])
	content = in_.read()
	in_.close()
	conf = json.loads(content.decode() if isinstance(content, bytes) else content)
	wlt = wallet.Wallet(conf["forging"]["secret"][0])
elif options.secret:
	wlt = wallet.Wallet(options.secret)
elif options.keyring:
	wlt = wallet.open(options.keyring)
else:
	raise Exception("Can not do something for now !")

print(wlt.address)

logfile = os.path.join(HOME, "Payment", "%s.pay" % datetime.datetime.now().strftime("%y-%m-%d %Hh%M"))
try: os.makedirs(os.path.dirname(logfile))
except: pass
log = open(logfile, "w")

wlt.update()
if wlt.delegate["rate"] > 51:
	log.write("%s is not an active delegate right now !" % wlt.delegate["username"])
	log.close()
	raise Exception("%s is not an active delegate right now !" % wlt.delegate["username"])
	
elif wlt.balance < 200:
	log.write("%s does not have more than 200 Arks !" % wlt.delegate["username"])
	log.close()
	raise Exception("%s does not have more than 200 Arks !" % wlt.delegate["username"])

def _ceilContributors(contributors, max_ratio):
	total_vote = sum(contributors.values())
	cut_vote = max_ratio*total_vote
	return dict([a,cut_vote if v/total_vote > max_ratio else v] for a,v in contributors.items())

def _getVoteFidelity(contributors, delay=30):
	now = datetime.datetime.now(slots.UTC)
	delta = datetime.timedelta(days=delay)
	total_second = delta.total_seconds()
	limit = now - delta
	timestamp_limit = slots.getTime(limit)
	public_key = wlt.publicKey
	fidelity = {}
	print("Checking %s-day-fidelity from vote history...\n" % delay)
	for addr in contributors:
		data = api.Transaction.getTransactionsList(senderId=addr, orderBy="timestamp:desc").get("transactions", [])
		if len(data):
			while data[-1]["timestamp"] > timestamp_limit:
				search = api.Transaction.getTransactionsList(senderId=addr, orderBy="timestamp:desc", offset=len(data)).get("transactions", [])
				data += search
				if len(search) < 50:
					break
			tx_3 = [t for t in data if t["type"] == 3]
			details = sorted([[t["timestamp"], t["asset"]["votes"][0][0]] for t in tx_3 if t["timestamp"] >= timestamp_limit and public_key in t["asset"]["votes"][0] and t["senderId"] != wlt.address], key=lambda e:e[0])

		if len(details):
			cumul = 0.
			start = timestamp_limit
			for elem in details:
				if elem[-1] == "+": start = elem[0]
				else: cumul += elem[0] - start
			if elem[-1] == "+": cumul += slots.getTime(now) - start
			fidelity[addr] = cumul/total_second
		else:
			fidelity[addr] = 1.0
	return fidelity

contributors = dict((v["address"],int(v["balance"])) for v in wlt.voters)
contributors = _ceilContributors(contributors, 70./100)
fidelity = _getVoteFidelity(contributors.keys(), delay=7)
contributors = dict([addr,vote*fidelity[addr]] for addr,vote in contributors.items())
k = 1.0/max(1.0, sum(contributors.values()))
contributors = dict([addr,vote*k] for addr,vote in contributors.items())

amount = wlt.balance
log.write("delegate amount : A%.8f\n" % amount)
header = ["Date", datetime.datetime.now(), ""]
content = ["ARK amount", amount, ""]

# ARK to be exchanged for node fees payment
node_invest = 2*math.ceil(USD2ARK(__daily_fees__*7)) - __tx_fee__
log.write("node fees       : A%.8f\n" % node_invest)
header.append("Node fees")
content.append(node_invest)
wlt.sendArk(node_invest, __exchange__)

# part to be distributed
share = amount - node_invest
log.write("Share           : A%.8f\n" % share)

pythoners = 0.10*share - __tx_fee__
log.write("For pythoners   : A%.8f\n" % pythoners)
header.append("Pythoners")
content.append(pythoners)
wlt.sendArk(pythoners, __pythoners__)

investments = 0.65*share - __tx_fee__
log.write("For investments : A%.8f\n" % investments)
header.append("Investments")
content.append(investments)
wlt.sendArk(investments, __investments__)

voters = 0.25*share
log.write("For voters      : A%.8f [checksum:%f]\n" % (voters, sum(contributors.values())))

log.write("\nArky contributors :\n")
header.append("")
content.append("")
for addr,ratio in contributors.items():
	amount = voters*ratio - __tx_fee__
	if amount > 0.:
		wlt.sendArk(amount, addr, vendorField="Arky weekly interests. Thanks for your contribution !")
		log.write("%s [fidelity:%f]: A%.8f\n" % (addr, fidelity[addr], amount))
		header.append(addr)
		content.append(amount)
	else:
		log.write("%s [fidelity:%f]: not enough ark to share\n" % (addr, fidelity[addr]))
		header.append(addr)
		content.append("-")

out = open("accounting.csv", "a")
out.write(";".join(["%s"%e for e in header])  + "\n")
out.write(";".join(["%s"%e for e in content]) + "\n")
out.close()

wallet.mgmt.join()
log.close()
