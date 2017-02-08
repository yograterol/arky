# -*- encoding: utf8 -*-
# © Toons

import json, requests
from .. import setInterval


def getKrakenPair(pair):
	data = json.loads(requests.get("https://api.kraken.com/0/public/Ticker?pair="+pair.upper()).text)
	A, B = pair[:3], pair[3:]
	A = ("Z" if A in ['USD', 'EUR', 'CAD', 'GPB', 'JPY'] else "X") + A
	B = ("Z" if B in ['USD', 'EUR', 'CAD', 'GPB', 'JPY'] else "X") + B
	try: return float(data["result"][A + B]["c"][0])
	except: return -1

def getArkPrice(curency):
	try: cmc_ark = json.loads(requests.get("http://coinmarketcap.northpole.ro/api/v5/ARK.json").text)
	except: cmc_ark = {"price": {"usd":1/34}}
	return float(cmc_ark["price"][curency])


def getPoloniexPair(pair):
	if "_" not in pair: pair = pair[:3] + "_" + pair[3:]
	return float(poloniex_json[pair]["last"])

# poloniex global data 
# reload data every 30 seconds
@setInterval(30) 
def load():
	global poloniex_json
	poloniex_json = json.loads(requests.get("https://poloniex.com/public?command=returnTicker").text)
load()
