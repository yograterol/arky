.. image:: https://github.com/Moustikitos/arky/raw/master/ark-logo.png
   :target: https://ark.io
   :width: 100

**Arky** is the Python API for `ARK ecosystem`_.

Copyright 2015-2016, **Toons**, `BSD licence`_

Install
=======

Ubuntu
^^^^^^

Open a terminal and type : ``sudo pip install arky`` or ``sudo pip3 install arky``


Windows 
^^^^^^^

Run a command as Administrator and type : ``pip install arky``

Using ``arky``
==============

Select network
^^^^^^^^^^^^^^

You need to import ``api`` module first and eventualy change from ``testnet`` (default) via ``api.use`` function.

>>> from arky import api
>>> api.use("ark")

``arky.core``
^^^^^^^^^^^^^

>>> from arky import core
>>> core.api.use("ark") # api is loaded by core

``core`` module allows python developpers to interact with ARK ecosystem.

>>> keys = core.getKeys("secret")
>>> keys.public.hex()
'03a02b9d5fdd1307c2ee4652ba54d492d1fd11a7d1bb3f3a44c4a05e79f19de933'
>>> keys.wif
'SB3BGPGRh1SRuQd52h7f5jsHUg1G9ATEvSeA7L5Bz4qySQww4k7N'
>>> core.getAddress(keys)
'AJWRd23HNEhPLkK1ymMnwnDBX2a7QBZqff'
>>> tx = core.Transaction(amount=100000000, recipientId="AQpqHHVFfEgwahYja9DpfCrKMyMeCuSav4")
>>> tx.sign("secret")
>>> tx.serialize()
{'recipientId': 'AQpqHHVFfEgwahYja9DpfCrKMyMeCuSav4', 'timestamp': 20832330, 'amount': 100000000, 'a
sset': {}, 'senderPublicKey': '03a02b9d5fdd1307c2ee4652ba54d492d1fd11a7d1bb3f3a44c4a05e79f19de933', 
'fee': 10000000, 'signature': '304402201dbf20a62d3411c6d000b691edf3ed50c34baa96b94dedf70e2d512b9f917
8250220475869560dd9740e2c324972be3cb2690e5fdd27b1cccf6dcd8fb325f52f8f25', 'type': 0, 'id': '16683123
258705133772'}
>>> core.sendTransaction(tx)

More on ``arky.core`` ?

>>> help(core)

``arky.api``
^^^^^^^^^^^^

>>> from arky import api
>>> api.use("ark")
>>> api.Account.getAccount('AR1LhtKphHSAPdef8vksHWaXYFxLPjDQNU')
{'success': True, 'account': {'secondSignature': 0, 'unconfirmedBalance': '10085162955069', 'balanc
e': '9668858747506', 'secondPublicKey': None, 'publicKey': '0326f7374132b18b31b3b9e99769e323ce1a4ac
5c26a43111472614bcf6c65a377', 'u_multisignatures': [], 'unconfirmedSignature': 0, 'address': 'AR1Lh
tKphHSAPdef8vksHWaXYFxLPjDQNU', 'multisignatures': []}}

More on ``arky.api`` ?

>>> help(api)

``arky.mgmt``
^^^^^^^^^^^^^

>>> from arky import mgmt

``mgmt`` deploys threaded transaction managment. Threads are automaticaly launched with ``mgmt`` module import.

>>> mgmt.THREADS
[<TxMGMT(Thread-1, started 2436)>, <TxMGMT(Thread-2, started 5832)>, <TxLOG(Thread-3, started 6580)>]

To send a transaction :

>>> tx = core.Transaction(amount=100000000, recipientId="AQpqHHVFfEgwahYja9DpfCrKMyMeCuSav4")
>>> mgmt.push(tx, "secret")
>>> tx = core.Transaction(amount=100000000, recipientId="AQpqHHVFfEgwahYja9DpfCrKMyMeCuSav4", secret="secret")
>>> mgmt.push(tx) # no secret needed here

Then, check into the ``.arky.mgmt`` logfile into your `home` directory :

::

  ...
  [2017-02-11 20:16:02,721] success:True - transaction:<1.00000000 ARK signed transaction type 0 from AJWRd23HNEhPLkK1ymMnwnDBX2a7QBZqff to AQpqHHVFfEgwahYja9DpfCrKMyMeCuSav4> - transactionIds:['df65053eea80fa4ce035c79698554f725f189ee653c474bbf722df99cf513ebe']

To stop threads :

>>> mgmt.stop()
>>> mgmt.THREADS
[<TxMGMT(Thread-1, stopped 2436)>, <TxMGMT(Thread-2, stopped 5832)>, <TxLOG(Thread-3, stopped 6580)>]

To start threads, you may change thread number for transaction managment :

>>> mgmt.cfg.__NB_THREAD__ = 1 # only one TxMGMT thread
>>> mgmt.start()
>>> mgmt.THREADS # last thread is always a TxLOG
[<TxMGMT(Thread-4, started 1988)>, <TxLOG(Thread-5, started 6240)>]


``arky.wallet``
^^^^^^^^^^^^^^^

>>> from arky import wallet
>>> wallet.api.use("ark") # api is loaded by wallet

``Wallet`` class allows developper to send ARK, to register address as delegate and to vote for delegates.

>>> w = wallet.Wallet("secret")
>>> w.delegate
False
>>> w.registered
False
>>> w.balance
1076464600000
>>> w.candidates # valid username that can be up/down voted
['techbytes', '4miners.net', 'kostik', 'boldninja', 'sonobit', 'marco229', 'dotnet70', 'arkfuturesma
rtnode', 'dafty', 'tibonos', 'jamiec79', 'sidzero', 'ghostfaceuk', ..., 'densmirnov', 'ark_faucet', 
'wes2', 'deskbobtwo', 'wes4', 'genesis_13']
>>> w.save("secret.wlt")
>>> w2 = wallet.open("secret.wlt")
>>> w2.balance
1076464600000
>>> w2.voteDelegate(up=["arky", "ravelou"])
>>> w2.votes
['ravelou', 'arky']
>>> w2.voteDelegate(down=["arky"])
>>> w2.votes
['ravelou']

More on ``arky.wallet`` ?

>>> help(wallet)

Support this project
====================

.. image:: http://bruno.thoorens.free.fr/img/bitcoin.png
   :width: 100

``3Jgib9SQiDLYML7QKBYtJUkHq2nyG6Z63D``

``16SPHzxaxjCYccnJCRY3RG711oybQj4KZ4``


Create your delegate
====================

.. image:: https://github.com/Moustikitos/arky/raw/master/vultr-logo.png
   :target: http://www.vultr.com/?ref=7071726
   :width: 100


.. _ARK ecosystem: https://github.com/ArkEcosystem
.. _BSD licence: http://htmlpreview.github.com/?https://github.com/Moustikitos/arky/blob/master/arky.html
