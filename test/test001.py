# -*- encoding:utf-8 -*-
from arky import core, mgmt, api, ArkyDict
import requests, json, binascii, time

core.use("ark")
core.cfg.__URL_BASE__ = "http://167.114.43.46:4000"
core.cfg.__HEADERS__['nethash'] = "7dc9f1ef941e55dcc741f026634a484fd4c4e6c925d1050ffd758087ff0021ea"

for i in range(10):
	tx = core.Transaction(amount=100000000, recipientId="Aa4EzB5JtEaUWRgfbzXfm7CxhX3WsaDKwt", vendorField="arky Python API test")
	mgmt.push(tx, "secret", None)
	time.sleep(0.5)

mgmt.stop()
