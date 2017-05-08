.. image:: https://github.com/Moustikitos/arky/raw/master/arky-logo.png
   :target: https://ark.io

Copyright 2016-2017 **Toons**, Copyright 2017 **ARK**, `MIT licence`_

Install
=======

Ubuntu
^^^^^^

Open a terminal and type :

``sudo pip install arky``

If you work with ``python3``

``sudo pip3 install arky``

From development version

``sudo -H pip install git+https://github.com/ArkEcosystem/arky.git``

If you work with ``python3``

``sudo -H pip3 install git+https://github.com/ArkEcosystem/arky.git``

Windows 
^^^^^^^

Run a command as Administrator and type :

``pip install arky``

For development version

``pip install git+https://github.com/ArkEcosystem/arky.git``

Using ``arky``
==============

``arky`` relies on three major elements
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**api package**

``api`` package allows developpers to send requests to the blockchain according
to `ARK API`_. For security reason only ``GET`` methods are implemented in
``api`` package.

>>> from arky import api
>>> api.use("ark")
>>> api.Account.getAccount('AR1LhtKphHSAPdef8vksHWaXYFxLPjDQNU')
{'success': True, 'account': {'secondSignature': 0, 'unconfirmedBalance': '10085162955069', 'balanc
e': '9668858747506', 'secondPublicKey': None, 'publicKey': '0326f7374132b18b31b3b9e99769e323ce1a4ac
5c26a43111472614bcf6c65a377', 'u_multisignatures': [], 'unconfirmedSignature': 0, 'address': 'AR1Lh
tKphHSAPdef8vksHWaXYFxLPjDQNU', 'multisignatures': []}}

More on ``arky.api`` ?

>>> help(api)

**core module**

>>> from arky import core
>>> core.api.use("ark") # api is loaded by core

``core`` module allows developpers to access core functions.

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

**wallet module**

>>> from arky import wallet
>>> wallet.api.use("ark") # api is loaded by wallet

``Wallet`` class allows developpers to send ARK, register address as delegate
and vote for delegates.

>>> w = wallet.Wallet("secret")
>>> w.delegate
False
>>> w.registered
False
>>> w.balance
10764.646
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

Easy way to use ``arky``
^^^^^^^^^^^^^^^^^^^^^^^^

``arky-cli`` is command line interface that simplify interaction with ARK
blockchain. Once script is executed, it loads all needed environment to execute
simple commands. Type ``exit`` to close the interface.

`Arky Command Line Interface`_

Authors
=======

Toons <moustikitos@gmail.com>

Support this project
====================

.. image:: https://github.com/ArkEcosystem/arky/raw/master/ark-logo.png
   :height: 30

Toons Ark address: ``AUahWfkfr5J4tYakugRbfow7RWVTK35GPW``

.. image:: http://bruno.thoorens.free.fr/img/bitcoin.png
   :width: 100

Toons Bitcoin address: ``3Jgib9SQiDLYML7QKBYtJUkHq2nyG6Z63D``


**Show gratitude on Gratipay:**

.. image:: http://img.shields.io/gratipay/user/b_py.svg?style=flat-square
   :target: https://gratipay.com/~b_py

**Vote for Toons' delegate arky**

Version
=======

**0.1.8**

+ relative import fix for ``python v2.x``

+ updated testnet and devnet seeds

+ ``api`` pkg:
   * ``api.get`` improvement
   * ``api.use`` can now connect to a custom peer
   * ``api.broadcast`` improvement

**0.1.7**

+ ``api`` pkg :
   * documentation (docstring)
   * added ``api.send_tx`` and ``api.broadcast``
   * ``api.get`` code improvement
   * bugfix on requests header ``port`` field value 

+ ``core`` mod :
   * removed ``sendTransaction`` (use ``api.send_tx`` instead)
   * removed ``checkStrictDER`` calls in ``core.Transaction.sign``

**0.1.6**

+ ``api`` pkg : improve peer connection

**0.1.5**

+ ``wallet`` mod : code improvement
+ ``util`` pkg : https bug fix in frozen mode
+ ``api`` pkg : update

**0.1.4**

+ first mainnet release

.. _MIT licence: http://htmlpreview.github.com/?https://github.com/Moustikitos/arky/blob/master/arky.html
.. _ARK API: https://github.com/ArkEcosystem/ark-api
.. _Arky Command Line Interface: https://github.com/Moustikitos/arky-cli
