# -*- encoding:utf-8 -*-
from arky import core, api, slots
import os, re, sys, json, logging, binascii, smtplib 


# screen command line
from optparse import OptionParser
parser = OptionParser()
parser.set_usage("""usage: %prog actions [options]

Actions:
 update                 update node running on peer

 check                  check if node is running and forging""")
parser.add_option("-i", "--ip",                            dest="ip",                    help="peer ip you want to check")
parser.add_option("-e", "--email",                         dest="email",                 help="email for notification")
parser.add_option("-p", "--password",                      dest="password",              help="email password")
parser.add_option("-s", "--smtp-port",                     dest="smtp",                  help="smtp address+port to use")
parser.add_option("-m", "--mainnet", action="store_false", dest="testnet", default=True, help="switch on mainnet")
# parse command line
(options, args) = parser.parse_args()

# deal with network
if options.testnet:
	forever_start = "forever start app.js --genesis genesisBlock.testnet.json --config config.testnet.json"
	db_table = "ark_testnet"
else:
	forever_start = "forever start app.js --genesis genesisBlock.main.json --config config.main.json"
	db_table = "ark_mainnet"

# deal with home directory
if "win" in sys.platform:
	home_path = os.path.join(os.environ["HOMEDRIVE"], os.environ["HOMEPATH"])
elif "linux" in sys.platform:
	home_path = os.environ["HOME"]

# open the log file
logging.basicConfig(filename=os.path.join(home_path, 'delegate.log'), format='%(levelname)s:%(message)s', level=logging.INFO)

# first of all get delegate json data
# it automaticaly searches json configuration file in "/home/username/ark-node" folder
# if your install does not match this default one, you have to set ARKNODEPATH environement variable
def getConfig(json_path):
	in_ = open(json_path)
	content = in_.read()
	in_.close()
	return json.loads(content.decode() if isinstance(content, bytes) else content)

json_folder = os.environ.get("ARKNODEPATH", os.path.join(home_path, "ark-node"))
# move to ark node directory
os.chdir(json_folder)

try:
	json_testnet = getConfig(os.path.join(json_folder, "config.testnet.json"))
	json_mainnet = getConfig(os.path.join(json_folder, "config.main.json"))
except:
	logging.info('Can not find any peer')
	sys.exit()

def putSecrets():
	path_1 = os.path.join(json_folder, "config.testnet.json")
	path_2 = os.path.join(json_folder, "config.main.json")
	new_json_testnet = getConfig(path_1)
	new_json_mainnet = getConfig(path_2)
	new_json_testnet["forging"]["secret"] = json_testnet["forging"]["secret"]
	new_json_mainnet["forging"]["secret"] = json_mainnet["forging"]["secret"]
	in_1 = open(path_1, "w")
	json.dump(new_json_testnet, in_1, indent=2)
	in_1.close()
	in_2 = open(path_2, "w")
	json.dump(new_json_mainnet, in_2, indent=2)
	in_2.close()


# deal if launch from command line
if len(sys.argv) > 1: logging.info('### %s : delegate.py %s %s ###', slots.datetime.datetime.now(slots.UTC), args, options)
# add your peer ip here
else: options.ip = '45.63.114.19'

peer_version = api.Peer.getPeerVersion().get("version", "0.0.0")
block_height = api.Block.getBlockchainHeight().get("height", False)
try:
	public_key = binascii.hexlify(core.getKeys((json_testnet if options.testnet else json_mainnet)["forging"]["secret"][0]).public)
except:
	logging.info('Can not find any secret')
	sys.exit()

if isinstance(public_key, bytes): public_key = public_key.decode()

# retrieve info from ark.log
class ArkLog:
	@staticmethod
	def getLastSyncTime():
		search = re.compile(".* ([0-9]{2,4})-([0-9][0-9])-([0-9][0-9]) ([0-9][0-9]):([0-9][0-9]):([0-9][0-9]) .*")
		catch = os.popen('cat %s | grep "Finished sync" | tail -1' % os.path.join(json_folder, "logs", "ark.log")).read().strip()
		try: return slots.datetime.datetime(*[int(e) for e in search.match(catch).groups()], tzinfo=slots.UTC)
		except: return slots.BEGIN_TIME

	@staticmethod
	def getBlockchainHeight():
		search = re.compile(".* height: ([0-9]*) .*")
		catch = os.popen('cat %s | grep "Received height" | tail -1' % os.path.join(json_folder, "logs", "ark.log")).read().strip()
		try: return int(search.match(catch).groups()[0])
		except: return 0

	@staticmethod
	def getPeerHeight():
		search = re.compile(".* height: ([0-9]*) .*")
		catch = os.popen('cat %s | grep "Received new block id" | tail -1' % os.path.join(json_folder, "logs", "ark.log")).read().strip()
		try: return int(search.match(catch).groups()[0])
		except: return 0

# retrieve info from ark.api
def isActiveDelegate():
	search = [dlgt for dlgt in api.Delegate.getDelegates().get("delegates", []) if dlgt['publicKey'] == public_key]
	if not len(search): return False
	else: return search[0]

def getPeerInfo():
	search = [peer for peer in api.Peer.getPeersList().get("peers", []) if peer["ip"] == options.ip]
	if not len(search): return False
	else: return search[0]

def getLastForgedBlock():
	search = [blck for blck in api.Block.getBlocks().get("blocks", []) if blck["generatorPublicKey"] == public_key]
	if not len(search): return False
	else: return search[0]

delegate = isActiveDelegate()
# {'publicKey': '0326f7374132b18b31b3b9e99769e323ce1a4ac5c26a43111472614bcf6c65a377', 
# 'productivity': 90.28, 
# 'missedblocks': 74, 
# 'approval': 97.36, 
# 'address': 'AR1LhtKphHSAPdef8vksHWaXYFxLPjDQNU', 
# 'vote': '12176985772856181', 
# 'producedblocks': 687, 
# 'username': 'arky', 
# 'rate': 33}

peer = getPeerInfo()
# {'port': 4000, 
# 'blockheader': {
# 	'totalFee': 110000000, 
# 	'blockSignature': '3044022065f2ec850891d9ec758bb87e0c5735d6504534c33d4d6c1d32dbd5fa808baf6e02201b356f0034aaa8e5e0944ff8d728aeb07ed49b6cc57ffdfc68276ad183d8e0f2', 
# 	'generatorPublicKey': '02033620fcdf599d28086311e6afe38e47c3bc19d21c794cdf1e84d86c641536d7', 
# 	'totalAmount': 1100562472, 
# 	'timestamp': 21087328, 
# 	'previousBlock': '13303588543971858952', 
# 	'reward': 200000000, 
# 	'version': 0, 
# 	'payloadLength': 2214, 
# 	'numberOfTransactions': 11, 
# 	'payloadHash': '33aef88d6f6c5409ff5901ccc9dd94333cd10961adf7dd8226060b7cbb89334d', 
# 	'height': 37220, 'id': '1931410963195578193'
# }, 'state': 2, 
# 'os': 'linux4.4.19-1-pve', 
# 'string': '137.74.79.185:4000', 
# 'ip': '137.74.79.185', 
# 'height': 37220, 
# 'version': '0.2.0'}

last_block = getLastForgedBlock()
# {'totalForged': '200000000', 
# 'totalFee': 0, 
# 'blockSignature': '30450221009272f3dbe8af36db9c6f05e7044a6f0ae5a9002ec82aed458b83c9f95a04722602205808ef8c71b363197e763a0cb1819ee80dc3c232208ebc4c85fb034037db58f7', 
# 'generatorPublicKey': '03b15e462ac0505a8c524019096f8b550e15742336f5725f0de56df2669894b4e2', 
# 'confirmations': 1, 
# 'totalAmount': 0, 
# 'timestamp': 21090424, 
# 'numberOfTransactions': 0, 
# 'reward': 200000000, 
# 'version': 0, 
# 'payloadLength': 0, 
# 'previousBlock': '5019740463278951759', 
# 'generatorId': 'Aaoi7yd7d3MK3KZPKF49snLdbDBefQFPh2', 
# 'payloadHash': 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', 
# 'height': 37330, 
# 'id': '12753529974450248758'}

# testing functions
def isUpToDate():
	return "is up-to-date" in os.popen("git checkout").read().strip()

def isRunning():
	search = re.compile(".* app.js .* STOPPED.*")
	for line in os.popen('forever list').read().split("\n"):
		if search.match(line): return False
	return True

def isForging():
	logging.info('Checking peer delegate %s :', options.ip)
	if delegate:
		logging.info('%s is an active delegate : name=%s rate=%s productivity=%s%%', options.ip, delegate["username"], delegate["rate"], delegate['productivity'])

		if not peer:
			logging.info('It seems delegate network have some issues')
			return False

		if "blockheader" in peer:

			if "linux" in sys.platform:
				height_diff = block_height - ArkLog.getPeerHeight()
				sync_delay = (slots.datetime.datetime.now(slots.UTC) - ArkLog.getLastSyncTime()).total_seconds() / 60
				if sync_delay > (8*51*3):
					logging.info('%s seems not to be forging, peer synced %d minutes ago', options.ip, sync_delay)
					return False

				elif height_diff > 20:
					logging.info('%s seems not to be forging, peer height is %d blocks late', options.ip, height_diff)
					return False

			else:
				height_diff = block_height - peer['height']
				if height_diff > 20:
					logging.info('%s seems not to be forging, peer height is %d blocks late', options.ip, height_diff)
					return False

			logging.info('%s is forging !', options.ip)

			return True

		elif last_block:
			height_diff = block_height - last_block['height']
			block_delay = (slots.datetime.datetime.now(tzinfo=slots.UTC) - slots.getRealTime(int(last_block["timestamp"]))).to_seconds() / 60
			logging.info('%s seems not to be forging, last block synced %d minutes ago and is %d blocks late', options.ip, height_diff, block_delay)
			return False

		elif not isRunning():
			logging.info('%s seems is not forging, app.js just stopped', options.ip)
			logging.info('EXECUTE> %s [%s]', forever_start, os.popen(forever_start).read().strip())
			return False

		else:
			logging.info('%s seems not to be forging, last block not found', options.ip)
			return False

	else:
		logging.info('%s is not an active delegate', options.ip)
		return None

# action functions
def restartNode():
	logging.info('Restarting the node %s', options.ip)
	logging.info('EXECUTE> %s [%s]', "forever stopall", os.popen("forever stopall").read().strip())
	logging.info('EXECUTE> %s [%s]', forever_start,     os.popen(forever_start).read().strip())

def updateNode(droptable=False):
	logging.info('Checking if %s is up to date', options.ip)
	if not isUpToDate():
		logging.info(    'Updading node:')
		logging.info(    'EXECUTE> %s [%s]', "forever stopall",        os.popen("forever stopall").read().strip())
		if droptable:
			logging.info('EXECUTE> %s [%s]', "dropdb %s" % db_table,   os.popen("dropdb %s" % db_table).read().strip())
			logging.info('EXECUTE> %s [%s]', "createdb %s" % db_table, os.popen("createdb %s" % db_table).read().strip())
		logging.info(    'EXECUTE> %s [%s]', "git pull",               os.popen("git pull").read().strip())
		# putSecrets()
		logging.info(    'EXECUTE> %s [%s]', forever_start,            os.popen(forever_start).read().strip())
		return True # node updated
	logging.info('%s is up to date', options.ip)
	return False    # node already up to date

# email notification variable
notify = False
message = ""

# command line actions
if "update" in args:
	message += 'Subject: Update status\n\n'
	if updateNode():
		notify = True
		message += '<p>%s have been updated</p>\n' % options.ip

if "check" in args:
	message += 'Subject: Forging status\n\n'
	if not isForging():
		message += "<p>%s is not forging</p>\n" % options.ip
		notify = True
		if updateNode():
			message += "<p>%s have been updated</p>\n" % options.ip
			restartNode()

if len(sys.argv) > 1:
	logging.info('### end ###')

# print (options.smtp)
# send email notification
if notify and options.smtp:
	if "linux" in sys.platform:
		message += "<p>last log lines&nbsp;:</p>\n<pre>%s</pre>" % os.popen('cat %s | tail -30' % os.path.join(home_path, 'delegate.log')).read()

	server = smtplib.SMTP(options.smtp)
	server.ehlo()
	server.starttls()
	try:
		server.login(options.email, options.password)
		server.sendmail(
			options.email, 
			options.email, 
			'''from: Arky delegate manager <delegate@arky>
to: ARK delegate <%(email)s>
Content-Type: text/html
''' % {"email":options.email} + message)
	except:
		pass
