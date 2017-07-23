# -*- encoding: utf8 -*-
# © Toons

from .. import __PY3__, setInterval, ArkyDict, ROOT, cfg, api, core, util, cli, slots
from . import HISTORY
from yawTtk import dialog

import yawTtk, json, os, webbrowser


class DataView(yawTtk.Tree):

	rows = []
	headers = []

	def __init__(self, parent=None, cnf={}, **kw):
		yawTtk.Tree.__init__(self, parent, cnf, **kw)
		self.tag_configure("even", background="lavender")
		self.tag_configure("odd", background="lightblue")
		self.__data_headings = []
		self.__sort_meaning = ""

	def populate(self, sortkey=None, meaning=None):
		# clear data
		self.delete(*self.xchildren())
		if DataView.rows == None:
			return
		# check witch meaning use
		if meaning == None:
			meaning = "ASC" if self.__sort_meaning == "DESC" else "DESC"
			self.__sort_meaning = meaning
		# sort data if asked
		if sortkey != None:
			rows = sorted(DataView.rows, key=lambda e:e.get(sortkey, ""), reverse=True if meaning == "ASC" else False)
		else:
			rows = DataView.rows

		# manage headers
		if not len(self.__data_headings):
			if len(DataView.headers): self.__data_headings = DataView.headers
			else: self.__data_headings = list(rows[0].keys())
			self['columns'] = " ".join(["{%s}"%h for h in self.__data_headings])
		for i in range(len(self.__data_headings)):
			text = self.__data_headings[i]
			self.heading("#%d"%(i+1), text=text, command=lambda o=self,k=text: o.populate(k,None))
			self.column("#%d"%(i+1), anchor="center", stretch=1)

		# populate data
		even=False
		for row in rows:
			self.insert(value=tuple(row.get(k, "") for k in DataView.headers), tag=("even",) if even else ("odd",))
			even = not even


class KeyDialog(dialog.BaseDialog):

	passphrase1 = None
	passphrase2 = None
	address = None
	check = True

	def fillMainFrame(self):
		self.transient(self.master)
		self.mainframe.columnconfigure(1, weight=1, minsize=300)
		self.mainframe.rowconfigure(1, weight=1)

		yawTtk.Label(self.mainframe, image=dialog.password, compound="image", padding=(0,0,4,0)).grid(row=0, rowspan=4, column=0, sticky="new")
		yawTtk.Label(self.mainframe, text="Main passphrase").grid(row=0, column=1, sticky="nesw")
		self.secret = yawTtk.Entry(self.mainframe, show="-").grid(row=1, column=1, sticky="new")
		self.secret.focus()

		self.secondsecret = yawTtk.Entry(self.mainframe, show="-")
		if api.Account.getAccount(KeyDialog.address, returnKey="account").get('secondPublicKey', False):
			yawTtk.Label(self.mainframe, text="Second passphrase").grid(row=2, column=1, sticky="nesw")
			self.secondsecret.grid(row=3, column=1, sticky="nesw")
			self.title("Two-secret secured account")
		else:
			self.title("Single-secret secured account")

	def fillButton(self):
		yawTtk.Button(self.buttonframe, font=("tahoma", 8, "bold"), image=dialog.tick16, compound="left",
		              background=self.background, style="Dialog.TButton", default="active", text="Sign transaction", width=-1,
		              command=self.link).pack(side="right")
		b = yawTtk.Button(self.buttonframe, image=dialog.stop16, compound="left", text="Show",
		                  background=self.background, style="Dialog.Toolbutton", padding=(5,3))
		b.pack(side="left")
		b.bind("<ButtonPress>", lambda e,o=self: [o.secret.configure(show=""), o.secondsecret.configure(show="")])
		b.bind("<ButtonRelease>", lambda e,o=self: [o.secret.configure(show="-"), o.secondsecret.configure(show="-")])

	def show(self):
		KeyDialog.passphrase1 = None
		KeyDialog.passphrase2 = None
		dialog.BaseDialog.show(self)
		self.winfo_toplevel().wait_window(self)

	def link(self):
		passphrase1 = self.secret.get()
		passphrase2 = self.secondsecret.get()

		KeyDialog.passphrase1 = None if passphrase1 == "" else passphrase1
		KeyDialog.passphrase2 = None if passphrase2 == "" else passphrase2

		self.destroy()

		if KeyDialog.passphrase1 == None:
			KeyDialog.check = False
		elif core.getAddress(core.getKeys(KeyDialog.passphrase1)) == KeyDialog.address:
			KeyDialog.check = True
		else:
			KeyDialog.check = False


class AddressPannel(yawTtk.Frame):

	def __init__(self, master=None, cnf={}, **kw):

		config = dict(cnf, **kw)
		self.address = config.pop("address", False)
		yawTtk.Frame.__init__(self, master, **config)

		if not self.address: 
			raise Exception("No address given")


class AmountFrame(AddressPannel):

	def __init__(self, master=None, cnf={}, **kw):
		AddressPannel.__init__(self, master, cnf={}, **kw)
		self.columnconfigure(0, weight=0, minsize=35)
		self.columnconfigure(1, weight=1)
		self.columnconfigure(2, weight=0, minsize=120)

		self.amount = yawTtk.DoubleVar(self, 0., "%s.amount"%self._w)
		self.value = yawTtk.StringVar(self, u"\u0466 0.00000000", "%s.value"%self._w)
		self.what = yawTtk.StringVar(self, u"\u0466", "%s.what"%self._w)
		self.satoshi = 0

		yawTtk.Label(self, padding=2, text="amount", background="lightgreen", font=("tahoma", 8, "bold")).grid(row=0, column=0, columnspan=3, pady=4, sticky="nesw")
		yawTtk.Combobox(self, textvariable=self.what, state="readonly", values=(u"\u0466", "$", "€", "£", "¥", "%"), width=-1).grid(row=1, column=0, pady=4, sticky="nesw")
		yawTtk.Entry(self, textvariable=self.amount, justify="right").grid(row=1, column=1, padx=4, pady=4, sticky="nesw")
		yawTtk.Label(self, textvariable=self.value, relief="solid").grid(row=1, column=2, pady=4, sticky="nesw")

		self.amount.trace("w", self.update)
		self.what.trace("w", self.update)

	def update(self, *args, **kw):
		what = self.what.get()
		try: amount = self.amount.get()
		except: amount = 0.

		if what == "%":
			value = (float(api.Account.getBalance(self.address).get("balance", 0)) * amount/100 - cfg.__FEES__["send"])/100000000.
		elif what in ["$", "€", "£", "¥"]:
			price = util.getArkPrice({"$":"usd", "€":"eur", "£":"gbp", "¥":"cny"}[what])
			value = amount / price
		else:
			value = amount
		self.value.set("\u0466 %.8f" % value)
		self.satoshi = 100000000.*max(0., value)

	def get(self): return self.satoshi


class SendPannel(AddressPannel):
	
	def __init__(self, master=None, cnf={}, **kw):
		global HISTORY
		AddressPannel.__init__(self, master, cnf={}, **kw)

		self.rowconfigure(6, weight=1)
		#
		yawTtk.Label(self, padding=2, text="recipientId", background="lightgreen", font=("tahoma", 8, "bold")).grid(row=0, column=0, columnspan=3, padx=4, pady=4, sticky="nesw")
		self.recipientId = yawTtk.Combobox(self, values=tuple(HISTORY["send.addresses"])).grid(row=1, column=0, columnspan=3, padx=4, pady=4, sticky="nesw")
		
		#
		yawTtk.Label(self, padding=2, text="vendorField", background="lightgreen", font=("tahoma", 8, "bold")).grid(row=2, column=0, columnspan=3, padx=4, pady=4, sticky="nesw")
		self.vendorField = yawTtk.Entry(self).grid(row=3, column=0, columnspan=3, padx=4, pady=4, sticky="nesw")
		
		#
		self.amount = AmountFrame(self, padding=(4,0,4,4), address=self.address).grid(row=5, column=0, columnspan=3, sticky="nesw")
		
		#
		frame = yawTtk.Frame(self, padding=4, text="Send").grid(row=6, column=0, columnspan=3, sticky="esw")
		yawTtk.Separator(frame).pack(side="top", fill="x", pady=8)
		self.button = yawTtk.Button(frame, text="Send").pack(side="right")

	def getTransaction(widget):
		global HISTORY

		recipientId = widget.recipientId.get()
		if "send.addresses" not in HISTORY:
			HISTORY["send.addresses"] = [recipientId]
		elif recipientId not in HISTORY["send.addresses"]:
			HISTORY["send.addresses"].append(recipientId)

		return core.Transaction(
			amount=widget.amount.get(),
			recipientId=recipientId,
			vendorField=widget.vendorField.get()
		).serialize()


class VotePannel(AddressPannel):
	
	def __init__(self, master=None, cnf={}, **kw):
		AddressPannel.__init__(self, master, cnf={}, **kw)

		self.columnconfigure(0, weight=1)
		self.rowconfigure(6, weight=1)

		self.username = yawTtk.StringVar(self, "", "vote.username")

		#
		self.candidates = api.Delegate.getCandidates()
		yawTtk.Label(self, padding=2, text="delegate", background="lightgreen", font=("tahoma", 8, "bold")).grid(row=0, column=0, columnspan=3, padx=4, pady=4, sticky="nesw")
		self.delegate = yawTtk.Combobox(self, values=tuple(d["username"] for d in self.candidates), textvariable="vote.username").grid(row=1, column=0, columnspan=3, padx=4, pady=4, sticky="nesw")
	
		#
		frame = yawTtk.Frame(self, padding=4, text="Send").grid(row=6, column=0, sticky="esw")
		yawTtk.Separator(frame).pack(side="top", fill="x", pady=8)
		self.button = yawTtk.Button(frame, text="").pack(side="right")

		self.update()
		@setInterval(5)
		def _update(obj): obj.update()
		self._stop__update = _update(self)

	def update(self):
		vote = api.Account.getVotes(self.address, returnKey="delegates")
		if len(vote):
			self.delegate.set(vote[0]["username"])
			self.delegate.state("disabled")
			self.button["text"] = "Unvote"
			self.button.state("!disabled")
		else:
			self.delegate.state("!disabled")
			self.button["text"] = "Vote"
			self.button.state("disabled" if self.username.get() == "" else "!disabled")

	def getTransaction(widget):
		username = widget.username.get()
		if widget.button["text"] == "Unvote":
			return core.Transaction(
				type=3,
				recipientId = widget.address,
				asset=ArkyDict(votes=["-"+d["publicKey"] for d in widget.candidates if d["username"] == username])
			).serialize()
		else:
			return core.Transaction(
				type=3,
				recipientId = widget.address,
				asset=ArkyDict(votes=["+"+d["publicKey"] for d in widget.candidates if d["username"] == username])
			).serialize()

	def destroy(self):
		self._stop__update.set()
		yawTtk.Frame.destroy(self)


class TransactionPannel(yawTtk.Frame):

	def __init__(self, master=None, cnf={}, **kw):
		AddressPannel.__init__(self, master, cnf={}, **kw)
		self.columnconfigure(0, weight=1)
		self.rowconfigure(0, weight=1)

		self.tree = DataView(self, padding=0, show="headings").grid(row=0, column=0, sticky="nesw")
		self.tree.bind("<Double-Button-1>", lambda e,obj=self:obj.openTx(e))

		yawTtk.Autoscrollbar(self, target=self.tree, orient="horizontal").grid(row=1, column=0, sticky="nesw")
		yawTtk.Autoscrollbar(self, target=self.tree, orient="vertical").grid(row=0, column=1, sticky="nesw")

		DataView.headers = ["id", "date", "type", "amount", "senderId", "recipientId", "vendorField"]

		self.update()
		@setInterval(20)
		def _update(obj): obj.update()
		self._stop__update = _update(self)

	def openTx(self, event):
		widget = event.widget
		values = widget.item(widget.identify("item", event.x, event.y), "values")
		if values: webbrowser.open(cfg.__EXPLORER__ + "/tx/" + values[0])

	def update(self):
		data1 = api.Transaction.getTransactionsList(returnKey="transactions", senderId=self.address, orderBy="timestamp:desc", limit=50)
		data2 = api.Transaction.getTransactionsList(returnKey="transactions", recipientId=self.address, orderBy="timestamp:desc", limit=50)
		if len(data1) + len(data2) > len(DataView.rows):
			typ = {0:"send", 1:"register 2nd secret", 2:"register delegate", 3:"vote", 4:""}
			for row in data1:
				row["amount"] /= 100000000.
				row["date"] = slots.getRealTime(row.pop("timestamp"))
				row["type"] = typ[row["type"]]
			typ[0] = "receive"
			for row in data2:
				row["amount"] /= 100000000.
				row["date"] = slots.getRealTime(row.pop("timestamp"))
				row["type"] = typ[row["type"]]
			DataView.rows = data1 + data2
			self.tree.populate()

	def destroy(self):
		self._stop__update.set()
		yawTtk.Frame.destroy(self)




# 

class SharePannel(yawTtk.Frame):
	
	def __init__(self, master=None, cnf={}, **kw):
		AddressPannel.__init__(self, master, cnf={}, **kw)


