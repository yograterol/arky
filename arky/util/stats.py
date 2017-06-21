# -*- encoding: utf8 -*-
# © Toons

from .. import api, slots
import datetime

try:
	from matplotlib import pyplot as plt
	__MATPLOTLIB__ = True
except:
	__MATPLOTLIB__ = False


def plot2D(*points, **kw):
	if __MATPLOTLIB__:
		xlabel = kw.pop("xlabel", None)
		ylabel = kw.pop("ylabel", None)
		title = kw.pop("title", None)

		plt.plot([p[0] for p in points], [p[1] for p in points], **kw)
		for x, y, label in [p for p in points if len(p) == 3]: plt.annotate(label, (x, y))

		if xlabel: plt.xlabel(xlabel)
		if ylabel: plt.ylabel(ylabel)
		if title: plt.title(title)
		plt.show()

def getHistory(address, timestamp=0):
	# get all inputs
	tx_in = api.Transaction.getTransactionsList(recipientId=address, returnKey="transactions", limit=50, orderBy="timestamp:desc")
	if isinstance(tx_in, list) and len(tx_in):
		while tx_in[-1]["timestamp"] >= timestamp:
			search = api.Transaction.getTransactionsList(recipientId=address, returnKey="transactions", limit=50, offset=len(tx_in), orderBy="timestamp:desc")
			tx_in.extend(search)
			if len(search) < 50:
				break

		# get all outputs
		tx_out = api.Transaction.getTransactionsList(senderId=address, returnKey="transactions", limit=50, orderBy="timestamp:desc")
		while tx_out[-1]["timestamp"] >= timestamp:
			search = api.Transaction.getTransactionsList(senderId=address, returnKey="transactions", limit=50, offset=len(tx_out), orderBy="timestamp:desc")
			tx_out.extend(search)
			if len(search) < 50:
				break

		tx_in += [t for t in tx_out if t not in tx_in]
	elif not len(tx_in):
		raise Exception("Address has null transactions.")
	else:
		raise Exception(tx_in.get("error", "Api error"))
	return sorted([t for t in tx_in if t["timestamp"] >= timestamp], key=lambda e:e["timestamp"], reverse=True)

def getBalanceHistory(address, timestamp=0):
	balance = float(api.Account.getBalance(address, returnKey="balance"))/100000000.
	history = getHistory(address, timestamp)

	if not history:
		return [(slots.getRealTime(timestamp), balance), (datetime.datetime.now(slots.UTC), balance)]

	else:
		result = [(datetime.datetime.now(slots.UTC), balance)]
		for tx in history:
			result.insert(0, (slots.getRealTime(tx["timestamp"]), balance))
			balance += ((tx["fee"]+tx["amount"]) if tx["senderId"] == address else -tx["amount"])/100000000.
		result.insert(0, (slots.getRealTime(timestamp), balance))
		return result

def getVoteHistory(address, timestamp=0):
	history = [tx for tx in getHistory(address, timestamp) if tx["type"] == 3]
	candidates = dict([d["publicKey"], d["username"]] for d in api.Delegate.getCandidates())

	if not history:
		return []

	else:
		result = []
		for tx in history:
			pkey = tx["asset"]["votes"][0][1:]
			way = 0 if tx["asset"]["votes"][0][0] == "-" else 1
			result.insert(0, (slots.getRealTime(tx["timestamp"]), way, candidates[pkey]))
		return result

def getVoteForce(address, delay=30):
	now = datetime.datetime.now(slots.UTC)
	delta = datetime.timedelta(days=delay)
	timestamp_limit = slots.getTime(now - delta)

	# get actual balance and transaction history
	balance = float(api.Account.getBalance(address, returnKey="balance"))/100000000.
	history = getHistory(address, timestamp_limit)

	# if no transaction over periode integrate balance over delay and return it
	if not history:
		return balance*max(1.0, delta.total_seconds()/3600)

	end = slots.getTime(now)
	sum_ = 0.
	for tx in history:
		delta_t = (end - tx["timestamp"])/3600
		sum_ += balance * delta_t
		balance += ((tx["fee"]+tx["amount"]) if tx["senderId"] == address else -tx["amount"])/100000000.
		end = tx["timestamp"]
		if tx["type"] == 3:
			break

	if tx["type"] != 3:
		sum_ += balance * (tx["timestamp"]-timestamp_limit)/3600

	return sum_
