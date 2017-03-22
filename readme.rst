.. image:: https://github.com/Moustikitos/arky/raw/master/arky-logo.png
   :target: https://ark.io
   :width: 100

Copyright 2015-2016, **Toons**, `BSD licence`_

Install
=======

Ubuntu
^^^^^^

Open a terminal and type :

``sudo pip install arky``

If you work with ``python3``

``sudo pip3 install arky``

From development version

``sudo -H pip install git+https://github.com/Moustikitos/arky.git``

If you work with ``python3``

``sudo -H pip3 install git+https://github.com/Moustikitos/arky.git``

Windows 
^^^^^^^

Run a command as Administrator and type :

``pip install arky``

For development version

``pip install git+https://github.com/Moustikitos/arky.git``

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

**Use command line interface**

``arky-cli`` script provides a command line interface that simplify interaction
with ARK blockchain. Once script is executed, it loads all needed environment to
execute simple commands. Type ``exit`` to close the interface.

`Dowload arky CLI for windows x64`_

`Dowload arky CLI for windows x32`_

`Here is a FAQ`_ 

::

  arky-cli vx.y © Toons
  Here is a list of command

  -- execute --
  This command execute an arky script file.

  Usage: execute (<script>)

  -- connect --
      This command selects a specific node address to send requests to the
      blockchain. This action is not needed and is used only by developer.

  Usage: connect [<peer>]

  -- use --
      This command selects the network you want to work with. Two networks are
      presently available : ark and testnet. By default, command line interface
      starts on testnet.

  Usage: use (<network>)

  -- account --
      This command allows you to perform all kinds of transactions available
      within the ARK blockchain (except for multisignature) and to check some
      information.

      The very first step is to link to an ARK account using link subcommand
      below.

      Example:
      @ mainnet> account link secret
      AJWRd23HNEhPLkK1ymMnwnDBX2a7QBZqff @ mainnet>

      When account is linked, keys are registered locally in .keyring directory as
      an *.akr file according to PEM format. This way secret passphrases are only
      typed once and can not be read from disk.

      You can remove thoses files manually or via unlink or clear subcommand. No
      ARK are stored in *.akr files. Please note that *.akr files gives total
      access to associated an account within arky API.

      With send, split, share and support subcommands, there are three ways to
      define amount:
      1. ARK value (not in SATOSHI) using sinple float
      2. a percentage of the account balance using % symbol (63% will take 63
         percent of wallet balance)
      3. a currency value using $, £, € or ¥ symbol ($45.6 will be converted in
         ARK using coinmarketcap API)

  Usage: account link [[<secret> [<2ndSecret>]] | [-a <address>] | [-k <keyring>]]
         account save <keyring>
         account clear
         account unlink
         account status
         account balance
         account contributors
         account register <username>
         account register 2ndSecret <secret>
         account vote [-u <delegate>... | -d <delegate>...]
         account send <amount> <address> [<message>]
         account split <amount> <recipient>... [-m <message>]
         account share <amount> [-b <blacklist> -f <floor> -c <ceil> <message>]
         account support <amount> [<message>]

  Options:
  -u --up                                up vote all delegates name folowing
  -d --down                              down vote all delegates name folowing
  -b <blacklist> --blacklist <blacklist> comma-separated ark addresse list (no space)
  -a <address> --address <address>       already linked ark address
  -m <message> --message <message>       64-char message
  -k <keyring> --keyring <keyring>       a valid *.akr pathfile
  -f <floor> --floor <floor>             minimum treshold ratio to benefit from share
  -c <ceil> --ceil <ceil>                maximum share ratio benefit

  Subcommands:
      link         : link to account using secret passphrases, Ark address or
                     *.akr file. If secret passphrases contains spaces, it must be
                     enclosed within double quotes ("secret with spaces"). Note
                     that you can use address only for *.akr files registered
                     locally.
      save         : save linked account to an *.akr file.
      clear        : unlink account and delete all *.akr files registered locally.
      unlink       : unlink account and delete its associated *.akr file.
      status       : show information about linked account.
      balance      : show account balance in ARK.
      contributors : show voters contributions ([address - vote weight] pairs).
      register     : register linked account as delegate (cost 25 ARK);
                     or
                     register second signature to linked account (cost 5 ARK).
      vote         : up or/and down vote delegates from linked account.
      send         : send ARK amount to address. You can set a 64-char message.
      split        : equal-split ARK amount to different recipient. You can set a
                     64-char message.
      share        : share ARK amount with voters (if any) according to their
                     weight. You can set a 64-char message.
      support      : share ARK amount to relay nodes according to their vote rate.
                     You can set a 64-char message.

Support this project
====================

.. image:: http://bruno.thoorens.free.fr/img/bitcoin.png
   :width: 100

``3Jgib9SQiDLYML7QKBYtJUkHq2nyG6Z63D``

``16SPHzxaxjCYccnJCRY3RG711oybQj4KZ4``

.. image:: https://github.com/Moustikitos/arky/raw/master/ark-logo.png
   :height: 30

``APREAB1cyRLGRrTBs97BEXNv1AwAPpSQkJ``

Create your delegate
====================

.. image:: https://github.com/Moustikitos/arky/raw/master/vultr-logo.png
   :target: http://www.vultr.com/?ref=7071726
   :width: 100

.. _BSD licence: http://htmlpreview.github.com/?https://github.com/Moustikitos/arky/blob/master/arky.html
.. _ARK API: https://github.com/ArkEcosystem/ark-api
.. _Dowload arky CLI for windows x64: https://drive.google.com/file/d/0Bz6dDtWRLNUFYkJDc0NnWHdQdVE/view?usp=sharing
.. _Dowload arky CLI for windows x32: https://drive.google.com/file/d/0Bz6dDtWRLNUFUVo1bGY3R3BlcVk/view?usp=sharing
.. _Here is a FAQ: https://github.com/Moustikitos/arky/blob/master/wiki/arky-cli.md
