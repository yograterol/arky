# -*- encoding -*-
from arky.util import getArkPrice
from arky import api, wallet
import os, json, math, requests
api.use("ark")

__daily_fees__ = 5./30 # daily server cost
__pythoners__ = ""
__investments__ = ""
__exchange__ = ""

# screen command line
from optparse import OptionParser
parser = OptionParser()
parser.set_usage("usage: %prog arg1 ....argN [options]")
parser.add_option("-s", "--secret", dest="secret", help="wallet secret you want to use")
parser.add_option("-w", "--wallet", dest="wallet", help="wallet file you want to use")
(options, args) = parser.parse_args()

def ARK2USD(value): return value * getArkPrice("usd")
def USD2ARK(value): return value / getArkPrice("usd")

def getVoterContribution(wlt):
	data = {}
	total_votes = float(wlt.delegate["vote"])
	for voter in wlt.voters:
		voter_addr = voter["address"]
		nb_votes = len(api.Account.getVotes(voter_addr).get("delegates", []))
		data[voter_addr] = round(float(voter['balance'])/nb_votes/total_votes, 3)
	return data

if len(args) == 1 and os.path.exists(args[0]):
	in_ = open(args[0])
	content = in_.read()
	in_.close()
	conf = json.loads(content.decode() if isinstance(content, bytes) else content)
	wlt = wallet.Wallet(conf["forging"]["secret"][0])
elif options.secret:
	wlt = wallet.Wallet(secret)
elif options.wallet:
	wlt = wallet.open(options.wallet)
else:
	raise Exception("Can not do something for now !")

# do something
contributors = getVoterContribution(wlt)
amount = wlt.balance/100000000
print("amount         :", amount)
node_invest = 2*math.ceil(USD2ARK(__daily_fees__*7)) # ARK to be exchanged for node fees payment
# compute fees
fees = 0.1 * (len(contributors) + 3)
print("total fees     :", fees)
# part to be distributed
share = amount - node_invest - fees
print("share          :", share)
pythoners = 0.1*share
print("For pythoners  :", pythoners)
investments = 0.6*share
print("For investments:", investments)
voters = 0.3*share
print("For voters     :", voters)

print("\nTransfering ARK...")
for addr,ratio in contributors.items():
	print("sending", voters*ratio, "ARK to", addr)
	wlt.sendArk(voters*ratio, addr, vendorField="Arky weekly pay back. Thanks for you contribution !")

# wlt.sendArk(pythoners, __pythoners__)
# wlt.sendArk(investments, __investments__)
# wlt.sendArk(node_invest, __exchange__)

wallet.mgmt.join()
