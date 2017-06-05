# Escrowing account with `arky`

In `ark`, there are no multisignature account, only multisignature transactions.
So how can we set-up an escrow-managed account?

Account owner that whants to send ARK need an escrower to validate and broadcast it

## Basic idea

Ark secure account with second passphrase, so if there is a way that owner only holds
first one and escrower only holds second one it could do the job.

Fortunatly, it is possible. Owner only needs escrower public key to set up the second
passphrase. This process is entirely secure.

## How to do it with `arky`?

Since version `0.2.0` command line interface is merged with `arky`. So let say an owner
whants to setup an escrow account and ask someone to be its escrower:

 - owner passphrase: `twelve-word passphrase escrow does not know`
 - escrower passphrase: `twelve-word passphrase owner does not know`

### 1. owner asks escrower public key
 
Escrower runs:

```
>>> from arky import cli
>>> cli.start()
hot-dark@> escrow publickey "twelve-word passphrase owner does not know"
Here is the public key: 02f566e6afa0f4c87e0b605f75bb76f40f0812306bfb38a47f973edcb79f4f952d
Send this bublic key as is to the account owner
hot-dark@escrow>
```

and sends `02f566e6afa0f4c87e0b605f75bb76f40f0812306bfb38a47f973edcb79f4f952d` to owner

### 2. Owner register escrower signature

Owner runs:

```
>>> from arky import cli
>>> cli.start()
hot-dark@> escrow link "twelve-word passphrase escrow does not know"
hot-dark@escrow[DQuT4...5qDha]> register 02f566e6afa0f4c87e0b605f75bb76f40f0812306bfb38a47f973edcb79f4f952d
    broadcast     : 100.0%
    transactionIds: ['181ac925edb6b52ec1c6da435ad6181562b2eac4aeda0450145183556b7c5b29']
    success       : True
hot-dark@escrow[DQuT4...5qDha]>
```

### 3. Owner whants to send ARK:

Owner runs:

```
>>> from arky import cli
>>> cli.start()
hot-dark@> escrow link "twelve-word passphrase escrow does not know"
hot-dark@escrow[DQuT4...5qDha]> send 3.123456 DTywx2qNfefZZ2Z2bjbugQgUML7yhYEatX "My first escrowed transaction"
You can now give d76b9514d7b8c8b700e63118485c08c5ac78d9582b19987c7b0451b5d8bdb66d.ctx file to your escrow
hot-dark@escrow[DQuT4...5qDha]>
```

in `.coldtx/dark` folder is saved a cold transaction (ie it does not touched the network ever) named
`d76b9514d7b8c8b700e63118485c08c5ac78d9582b19987c7b0451b5d8bdb66d.ctx`. This file have to be sent to the
escrower (email, ftp, slack etc...). 

### 4. Escrower validate and bradcast the transaction

Once escrower saved `d76b9514d7b8c8b700e63118485c08c5ac78d9582b19987c7b0451b5d8bdb66d.ctx` in its
`.coldtx/dark` folder, he runs:

```
>>> from arky import cli
>>> cli.start()
hot-dark@> escrow link -e "twelve-word passphrase owner does not know"
hot-dark@escrow[b5a3d...9b17a]> validate
Cold transaction(s) found:
    1 - 037f79ce4e3d20da0350305b52b4b70583ebdb5995bf2f7f0681da7ec0e80f31
    2 - 438171ce1b986ca363df22802adb736f8a692118db26c6c1736582a806b4a558
    3 - 4d6cb10c045e1b3303a93b0568842633c615397fda277e8cdf169464f7145b3b
    4 - 583a963073ea226bfc643f20d57b94cfb404539a95363a1796570a186b03358e
    5 - 5cdba03b0407b5a69811dd5ab2b71850aeea0389c6be1ec90a638fe364f38012
    6 - 7643fe5123689c446bf18405905068158e184b540e88e47f5f34165cbbffad5b
    7 - 932005691771154fa1718bc735c1214777291d744c1857fa4f38d70e0ff172dd
    8 - 9f265dbf349df18e2ada05a701727657e29ee8ec3cb419f896f03fb3ec4afede
    9 - b336826435784400a7e6c74652c1e9c252b7a16277f7b9b2273bf064b9a84419
    10 - be6b155307671ffb15489507bbf0868560620a229d21c9a42bb015c93a5e210a
    11 - d76b9514d7b8c8b700e63118485c08c5ac78d9582b19987c7b0451b5d8bdb66d
    12 - e2a8f2ebfb787f58afadd9a5e6e83e7824c4098c92ff34dff5e58a06347e7979
Choose an item: [1-12]> 11
Broadcast <type-0 transaction(A3.12345600) from DQuT4...5qDha to DTywx...YEatX>? [y-n]> y
    broadcast     : 100.0%
    transactionIds: ['09563bc9f9fe387d1b130a8358454b20f4b6b90d75086c3b132a3230324822d4']
    success       : True
hot-dark@escrow[b5a3d...9b17a]>
```

[here is the transaction](https://dexplorer.arkcoin.net/tx/09563bc9f9fe387d1b130a8358454b20f4b6b90d75086c3b132a3230324822d4)
