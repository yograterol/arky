# Why should I use `arky-cli` ?

`arky-cli` is a command line interface to `arky` API, the python framework for
ARK blockchain. It contains a set of commands and subcommands to execute simple
tasks that would require several lines of python codes.

Basicaly, if you are not a python developer and you want to interact in 
different way than using the [desktop wallet](https://github.com/ArkEcosystem/ark-desktop/releases),
you should consider `arky-cli`.

**Use case #1 : interactive mode**

You want to do some basic checkings :

```
## Welcome to arky-cli vx.y © Toons ##
@ testnet> use ark
@ mainnet> account link "my secret between quotes"
AY9ho6i6LQ82D3VDkdP7yBjSWhNHWkMvHg @ mainnet> account contributors
    CONTRIBUTORADDRESS#1: 25.3
    CONTRIBUTORADDRESS#2: 50.6
    CONTRIBUTORADDRESS#3: 11.4
    CONTRIBUTORADDRESS#4: 12.7
AY9ho6i6LQ82D3VDkdP7yBjSWhNHWkMvHg @ mainnet> account balance
    confirmedbalance  : 1265312345189
    unconfirmedbalance: 1265312345189
AY9ho6i6LQ82D3VDkdP7yBjSWhNHWkMvHg @ mainnet> exit
```

**Use case #2 : execution mode**

You set an ARK delegate forging on the ARK blockchain and you want to do some
transaction weekly. Write an arky script file containing one `arky-cli` command
per line :

```
use ark
account link -w /path/to/a/keyring/file
account send $10 ARKADDRESS#1 "optional mesage message #1"
account send 65% ARKADDRESS#2 "optional mesage message #2"
account share 25% --ceil 60 --floor 5 "optional mesage message #3"
account support 10% "optional mesage message #4"
```

And execute script : `python3 arky-cli.py --script /path/to/script/file`

The command line above can be set in a [`cron`](https://doc.ubuntu-fr.org/cron)
task on your delegate VPS so you do not have to run it yourself every week.

# What can I do with `arky-cli` ?

You can send every kind of transaction defined by ARK blockchain except
multisignature, you can check informations about your ARK addresses and you
can do some meta-transactions.

  - Transactions
    - create an ARK address
    - register a second signature for an ARK address
    - register ARK address as a delegate
    - upvote or downvote a delegate
    - send ARK
  - Checkings
    - balance of ARK address
    - votes made with the ARK address
    - votes received by ARK address
    - account or delegate status
  - Meta-transactions
    - split ARK amount between differents ARK addresses
    - share ARK amount between voters
    - support relay nodes sending ARK amount according to their vote weight

First thing to know if you want to go further is there are two ARK networks, one
for developers named `testnet` and one for the real world named `mainnet`.
`arky-cli` is connected to `testnet` on startup so you have to swich first.

```
## Welcome to arky-cli vx.y © Toons ##
@ testnet> use ark
@ mainnet> 
```

Remember that prompt will always show you where you are when you run a command.

# Do i need Python installed ? How do I run it ?

For Windows, `arky-cli` is available as a standalone binary so you do not have
to worry about python stuff. Once it is installed just run :

  * For interactive mode : `arky-cli`
  * For execution mode : `arky-cli --script /path/to/script/file`

For linux, most of distribution include `python3`. Just install `arky` API 
[using `pip3`](https://pip.pypa.io/en/stable) and run :

  * For interactive mode : `python3 -m arky-cli`
  * For execution mode : `python3 -m arky-cli --script /path/to/script/file`

For other platforms you will need to install `Python 3.x` and execute the
`python` binary with either `-m arky-cli` (interactive mode) or
`-m arky-cli --script /path/to/script/file` (execution mode) parameters.

# I want to create an account, what do I do ?

There is nothing to do to create an ARK account except remembering a secret. In
ARK blockchain, an address exists once it receive its firts ARKs. It just have
to be a valid address.

```
@ mainnet> account link "my secret between quotes"
AY9ho6i6LQ82D3VDkdP7yBjSWhNHWkMvHg @ mainnet> account balance
Account not linked or does not exist in blockchain yet
```

Send ARK to AY9ho6i6LQ82D3VDkdP7yBjSWhNHWkMvHg, asking someone or using exchange
sites, and your account is ready. If you forget secret `"my secret between quotes"`
you will never ever access AY9ho6i6LQ82D3VDkdP7yBjSWhNHWkMvHg.

# Are wallet or ARK stored localy ?

No, `arky-cli` writes a transaction history into `tx.log` and stores on linking
a keyring file to allow transactions signature. All those files can be removed
manualy without any risks for your accounts.

# I see in exemple above it can send $ or %, what is that actualy ?

When you want to define amount of a transaction, there are three ways:

  1. Giving a float value corresponding to the ARK amount you want to send.

  2. Giving a currency-style value. This value is transformed into equivalent
     ARK amount using [coinmarketcap API](https://coinmarketcap.com/api). It
     should be exchanged rapidly by the receiver because of market fluctuations.
     Available currency are $, £, € and ¥. € can not be used on Windows platform
     due to well known `cp850` encoding bug.

  3. Giving a percentage of total balance value to send, fees included.


# Where can I have more details about available commands ?

```
## Welcome to arky-cli vx.y © Toons ##
@ testnet> help
```
