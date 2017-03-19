# -*- encoding -*-
from arky import api, wallet, __PY3__
import os, json, datetime
api.use("ark")

# screen command line
from optparse import OptionParser
parser = OptionParser()
parser.set_usage("usage: %prog [JSON] [options]")
parser.add_option("-s", "--secret", dest="secret", help="wallet secret you want to use")
parser.add_option("-w", "--wallet", dest="wallet", help="wallet file you want to use")
(options, args) = parser.parse_args()

if len(args) == 1 and os.path.exists(args[0]):
	in_ = open(args[0])
	content = in_.read()
	in_.close()
	conf = json.loads(content.decode() if isinstance(content, bytes) else content)
	wlt = wallet.Wallet(conf["forging"]["secret"][0])
elif options.secret:
	wlt = wallet.Wallet(options.secret)
elif options.wallet:
	wlt = wallet.open(options.wallet)
else:
	raise Exception("Can not do something for now !")

# here you put ARK addresses and share you want to send
payment = {
	"AX8fQaCX73LR8DT8bAQ9atst7yDxcVhEfp": 0.60,
	"APW7bFmpzSQr7s9p56oo93ec2s6boDFZQY": 0.15,
	"Voters": 0.25
}
# put here ark voter addresse to be blacklisted
blacklist = []

if sum(payment.values()) > 1.0:
	raise Exception("Share is not fair enough")

if wlt.delegate["rate"] > 51:
	raise Exception("%s is not an active delegate right now !" % wlt.delegate["username"])

contributors = wlt.contributors
spare_ratio = 0.
for addr in [a for a in blacklist if a in contributors]: 
	spare_ratio += contributors.pop(addr)
spare_ratio /= len(contributors)
for addr in contributors:
	contributors[addr] += spare_ratio

total = wlt.balance

header = ["Date", datetime.datetime.now(), ""]
content = ["Amount", total, ""]

for addr,ratio in payment.items():
	if addr != "Voters":
		share = total*ratio - 0.1
		wlt.sendArk(share, addr, vendorField="your custom message here")
		header.append(addr)
		content.append(share)

if "Voters" in payment:
	header.append("")
	content.append("")
	amount = total*payment["Voters"]
	for addr,ratio in contributors.items():
		share = amount*ratio - 0.1
		if share > 0.:
			wlt.sendArk(share, addr, vendorField="your custom message to voters here")
		header.append(addr)
		content.append(share)

out = open("accounting.csv", "a")
out.write(";".join(["%s"%e for e in header])  + "\n")
out.write(";".join(["%s"%e for e in content]) + "\n")
out.close()

wallet.mgmt.join()
