# -*- encoding -*-
from arky.util import getArkPrice
from arky import api, wallet, HOME
import os, json, math, datetime
api.use("ark")

__daily_fees__ = 5./30 # daily server cost
__pythoners__ = 'APW7bFmpzSQr7s9p56oo93ec2s6boDFZQY'
__investments__ = 'AX8fQaCX73LR8DT8bAQ9atst7yDxcVhEfp'
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

logfile = os.path.join(HOME, "Payment", "%s.pay" % datetime.datetime.now().strftime("%y-%m-%d"))
try: os.makedirs(os.path.dirname(logfile))
except: pass
log = open(os.path.join(HOME, "Payment", "%s.pay" % datetime.datetime.now().strftime("%y-%m-%d")), "w")

amount = wlt.balance
log.write("delegate amount : A%.8f\n" % amount)
# ARK to be exchanged for node fees payment
node_invest = 2*math.ceil(USD2ARK(__daily_fees__*7))
log.write("node fees       : A%.8f\n" % node_invest)
contribution = wlt.contribution
fees = 0.1 * (len(contribution) + 3)
log.write("total fees      : A%.8f\n\n" % fees)

# part to be distributed
share = amount - node_invest - fees
log.write("Share           : A%.8f\n" % share)
pythoners = 0.15*share
log.write("For pythoners   : A%.8f\n" % pythoners)
investments = 0.6*share
log.write("For investments : A%.8f\n" % investments)
voters = 0.25*share
log.write("For voters      : A%.8f\n" % voters)

log.write("\nFor arky contributors :\n")
for addr,ratio in contribution.items():
	amount = voters*ratio
	if amount > 0.:
		log.write("%s : A%.8f\n" % (addr, amount))
		wlt.sendArk(amount, addr, vendorField="Arky weekly refund. Thanks for you contribution !")

wlt.sendArk(pythoners, __pythoners__)
wlt.sendArk(investments, __investments__)
# wlt.sendArk(node_invest, __exchange__)

wallet.mgmt.join()
