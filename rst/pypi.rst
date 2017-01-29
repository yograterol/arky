.. image:: https://github.com/Moustikitos/arky/raw/master/ark-logo.png
   :target: https://ark.io
   :width: 100

**Arky** is the Python API for `ARK ecosystem`_.

Copyright 2015-2016, **Toons**, `BSD licence`_

Install
=======

Ubuntu
^^^^^^

Open a terminal and type : ``sudo pip install arky``

Windows 
^^^^^^^

Run a command as Administrator and type : ``pip install arky``

Using ``arky``
==============

``arky`` allow python developpers to interact with ARK ecosystem. Testnet and mainnet are linkable
through ``switch`` function available at root of ``arky`` package.

>>> import arky
>>> arky.switch(False) # work on testnet (default)
>>> arky.switch(True)  # work on main net

``arky.api``
^^^^^^^^^^^^

>>> import arky.api as api
>>> api.Account.getAccount("AR1LhtKphHSAPdef8vksHWaXYFxLPjDQNU") # arky delegate
{'account': {'publicKey': '0326f7374132b18b31b3b9e99769e323ce1a4ac5c26a43111472614bcf6c65a377', 'bal
ance': '1101375294113', 'unconfirmedBalance': '1101375294113', 'u_multisignatures': [], 'unconfirmed
Signature': 0, 'secondSignature': 0, 'address': 'AR1LhtKphHSAPdef8vksHWaXYFxLPjDQNU', 'secondPublicK
ey': None, 'multisignatures': []}, 'success': True}

More on ``arky.api`` ?

>>> help(api)

``arky.core``
^^^^^^^^^^^^^

>>> import arky.core as core
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

Actualy, there is an issue with signature. ``sendTransaction`` uses a while loop to do several attempts :

>>> tx = core.Transaction(amount=1234000000, recipientId="AR1LhtKphHSAPdef8vksHWaXYFxLPjDQNU")
>>> core.sendTransaction("secret", tx)
{'transactionId': '3684489509227507694', 'attempt': 5, 'success': True}

More on ``arky.core`` ?

>>> help(core)

``arky.wallet``
^^^^^^^^^^^^^^^

``Wallet`` class allows developper to send ARK, to register wallet as delegate and to vote for delegates.
For now, this class is highly experimental and should be used carefully.

>>> import arky.wallet as wlt
>>> w = wlt.Wallet("secret")
>>> w.delegate
False
>>> w.registered
False
>>> w.balance
1076464600000
>>> w.candidates # valid username that can be up/down voted
['techbytes', '4miners.net', 'kostik', 'boldninja', 'sonobit', 'marco229', 'dotnet70', 'arkfuturesma
rtnode', 'dafty', 'tibonos', 'jamiec79', 'sidzero', 'ghostfaceuk', 'lamar', 'thrice.pi', 'doweig', '
forrest', 'axente', 'dafricash', 'hagie', 'bioly', 'xujian', 'raspi3', 'arkomatic', 'samuray_test', 
'bcboilermaker', 'kushed.delegate', 'arkseed', 'jakethepanda', 'frank', 'frank2', 'ravelou', 'arky',
 'cannabanana', 'ondin', 'genesis_14', 'superwoot112', 'genesis_41', 'jamiec79rsp', 'genesis_38', 'g
enesis_7', 'genesis_35', 'ilgio', 'fanilla', 'nuevax', 'wes3', 'genesis_1', 'arkshare', 'lidware', '
atlass', 'genesis_27', 'genesis_20', 'genesis_36', 'genesis_48', 'genesis_29', 'genesis_45', 'genesi
s_39', 'genesis_8', 'genesis_18', 'genesis_6', 'genesis_32', 'genesis_4', 'genesis_19', 'genesis_16'
, 'genesis_30', 'genesis_42', 'genesis_22', 'genesis_51', 'genesis_44', 'genesis_9', 'genesis_21', '
genesis_37', 'genesis_46', 'genesis_5', 'genesis_49', 'genesis_24', 'genesis_43', 'genesis_25', 'gen
esis_15', 'wes', 'standby2', 'thatisme', 'genesis_2', 'genesis_31', 'genesis_33', 'genesis_50', 'bra
d', 'grajson', 'genesis_34', 'arkeology', 'genesis_23', 'trustament', 'arkwhale', 'genesis_12', 'gen
esis_3', 'bull', 'cryptonite', 'deskbob', 'vega', 'dafty2', 'wishxy', 'bcboilermaker1', 'genesis_17'
, 'genesis_26', 'genesis_40', 'genesis_10', 'blockexp', 'standby', 'ghaarte', 'genesis_47', 'genesis
_11', 'ark_taurus', 'globe', 'ghaarte2', 'genesis_28', 'arkonprime_odsejen', 'densmirnov', 'ark_fauc
et', 'wes2', 'deskbobtwo', 'wes4', 'genesis_13']
>>> w.save("secret.wlt")
>>> w2 = wlt.Wallet.open("secret.wlt")
>>> w2.balance
1076464600000

More on ``arky.wallet`` ?

>>> help(wlt)

``delegate.py``
^^^^^^^^^^^^^^^

For the lucky 51 delegates forging on the ARK mainnet, ``arky`` package provides command line python script to monitor running peer.
``delegate.py`` is experimental and use it knowing what you do and how ARK net works.

``python -m delegate -h``

::

  Usage: delegate.py actions [options]

  Actions:
   update                 update node running on peer

   check                  check if node is running and forging

  Options:
    -h, --help            show this help message and exit
    -i IP, --ip=IP        peer ip you want to check
    -e EMAIL, --email=EMAIL
                          email for notification
    -p PASSWORD, --password=PASSWORD
                          email password
    -s SMTP, --smtp-port=SMTP
                          smtp address+port to use
    -m, --mainnet         switch on mainnet

To use ``delegate.py`` as node monitoring tool on Ubuntu, edit your cron tasks :

``crontab -e``

::

  # Edit this file to introduce tasks to be run by cron.
  #
  # Each task to run has to be defined through a single line
  # indicating with different fields when the task will be run
  # and what command to run for the task
  #
  # To define the time you can provide concrete values for
  # minute (m), hour (h), day of month (dom), month (mon),
  # and day of week (dow) or use '*' in these fields (for 'any').#
  # Notice that tasks will be started based on the cron's system
  # daemon's notion of time and timezones.
  #
  # Output of the crontab jobs (including errors) is sent through
  # email to the user the crontab file belongs to (unless redirected).
  #
  # For example, you can run a backup of all your user accounts
  # at 5 a.m every week with:
  # 0 5 * * 1 tar -zcf /var/backups/home.tgz /home/
  #
  # For more information see the manual pages of crontab(5) and cron(8)
  #
  # m    h    dom mon dow   command
    0    */6  *   *   *     python3 ~/arky/delegate.py update -i 45.63.114.19 -e xxxxxxxxxxx@gmail.com -p xxxxxxxxxxxxxxxx -s smtp.gmail.com:587
    */31 *    *   *   *     python3 ~/arky/delegate.py check  -i 45.63.114.19 -e xxxxxxxxxxx@gmail.com -p xxxxxxxxxxxxxxxx -s smtp.gmail.com:587


Support this project
====================

.. image:: http://bruno.thoorens.free.fr/img/bitcoin.png
   :width: 100

``3Jgib9SQiDLYML7QKBYtJUkHq2nyG6Z63D``

``16SPHzxaxjCYccnJCRY3RG711oybQj4KZ4``

.. _ARK ecosystem: https://github.com/ArkEcosystem
.. _BSD licence: http://htmlpreview.github.com/?https://github.com/Moustikitos/arky/blob/master/arky.html
