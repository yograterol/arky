# -*- encoding: utf8 -*-
# © Toons

from .. import api, slots
import datetime

def getHistory(address, timestamp=0):
	# get all inputs
	tx_in = api.Transaction.getTransactionsList(recipientId=address, returnKey="transactions", limit=50, orderBy="timestamp:desc")
	if len(tx_in):
		while tx_in[-1]["timestamp"] >= timestamp:
			search = api.Transaction.getTransactionsList(recipientId=address, returnKey="transactions", limit=50, offset=len(tx_in), orderBy="timestamp:desc")
			tx_in.extend(search)
			if len(search) < 50:
				break

	# get all outputs
	tx_out = api.Transaction.getTransactionsList(senderId=address, returnKey="transactions", limit=50, orderBy="timestamp:desc")
	if len(tx_out):
		while tx_out[-1]["timestamp"] >= timestamp:
			search = api.Transaction.getTransactionsList(senderId=address, returnKey="transactions", limit=50, offset=len(tx_out), orderBy="timestamp:desc")
			tx_out.extend(search)
			if len(search) < 50:
				break
			
	return sorted([t for t in tx_in+tx_out if t["timestamp"] >= timestamp], key=lambda e:e["timestamp"], reverse=True)

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
