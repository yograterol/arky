# -*- encoding: utf8 -*-
# © Toons

from . import __PY3__
if not __PY3__: import api, cfg, slots, wallet, core
else: from . import api, cfg, slots, wallet, core

import os, json, sqlite3


class ColdStorage:

	def __init__(self, path, **kwargs):
		if not path.endswith(".cld"): path += ".cld"

		self.path = os.path.abspath(path)
		self.connexion = sqlite3.connect(self.path)
		self.save = self.connexion.commit
		self.connexion.row_factory = sqlite3.Row
		self.cursor = self.connexion.cursor()

		self.cursor.execute("CREATE TABLE IF NOT EXISTS wallets(address TEXT, account TEXT);")
		self.cursor.execute('CREATE TABLE IF NOT EXISTS transactions(type INT, "timestamp" INT, ammount INT, fee INT, senderId TEXT, senderPublicKey TEXT, recipientId TEXT, requesterPublicKey TEXT, asset TEXT, signature TEXT, signSignature TEXT, id TEXT);')
		self.cursor.execute('CREATE TABLE IF NOT EXISTS multisignatures(type INT, "timestamp" INT, ammount INT, fee INT, senderId TEXT, senderPublicKey TEXT, recipientId TEXT, requesterPublicKey TEXT, asset TEXT, signature TEXT, signSignature TEXT, id TEXT);')
		
		self.cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS wallet_index ON wallets(address);")
		self.cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS transactions_index ON transactions(id);")
		self.cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS multisignatures_index ON multisignatures(id);")

	def putWallet(self, wlt):
		if isinstance(wlt, wallet.Wallet):
			self.cursor.execute("INSERT OR REPLACE INTO wallets(address, account) VALUES(?,?);", (wlt.address, json.dumps(wlt.account)))
		else:
			req = api.Account.getAccount(wlt)
			if req.success:
				self.cursor.execute("INSERT OR REPLACE INTO wallets(address, account) VALUES(?,?);", (wlt, json.dumps(req.account)))
			else:
				return req

	def getWallet(self, addr):
		pass

	def put(self, tx, table="transactions"):
		if isinstance(tx, core.Transaction):
			data = tx.serialize()
		elif isinstance(tx, dict):
			data = arkydify(tx)
		sql = "INSERT OR REPLACE INTO %s(%s) VALUES (%s);" % (table, ', '.join(data.keys()), ', '.join("?"*len(data)))
		self.cursor.execute(sql, data.values())

	def get(self, id, table="transactions"):
		sql = "SELECT * FROM %s WHERE id=?;" % table
		self.cursor.execute(sql, (id,))
		return self.cursor.fetchall()

	def putMultisignatur(self, tx):
		return put(self, tx, "multisignatures")

	def getMultisignature(self, id):
		return get(self, tx, "multisignatures")


def freezeTx(tx):
	cs = ColdStorage(cfg.__NET__)
	cs.put(tx)

def warmTx(id):
	pass
