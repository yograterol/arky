# Quick start with `arky-cli`

`arky-cli` is a command line interface to `arky` API, the python framework for
ARK blockchain. It contains a set of commands and subcommands to execute simple
tasks that would require several lines of python codes.

Basicaly, if you are not a python developer and you want to interact in 
different way than using the [desktop wallet](https://github.com/ArkEcosystem/ark-desktop/releases),
you should consider `arky-cli`.

```
>>> from arky import cli
@dark>>> cli.start()
### arky-cli vx.y - [arky x.y.z embeded]
Available commands: escrow, network, delegate, account
hot@dark/>
```

Prompt will always show you where you are.

**Enter in a command set and exit from it**

To access a command set just enter its name, enter `..` or `exit` to exit from it. Typing `?` or `help`
will prompt available command set syntax.

```
hot@dark/> network
hot@dark/network> ..
hot@dark/> escrow
hot@dark/escrow> ?
Usage: escrow register <2ndPublicKey>
       escrow link [<secret> -e]
       escrow send <amount> <address> [<message>]
       escrow validate [<id>]
       escrow save <name>
       escrow unlink

Options:
-e --escrow  tag to link account as escrower

Subcommands:
    register  : set second signature using escrow public key.
    link      : link to delegate using secret passphrases. If secret passphrases
                contains spaces, it must be enclosed within double quotes
                ("secret with spaces"). If no secret given, it tries to link
                with saved escrow(s).
    send      : create cold transaction to send ARK if validated.
    validate  : broadcast cold transactions.
    save      : save linked escrow to a *.tok1 or *.tok2 file.
    unlink    : unlink from escrow.
hot@dark/escrow> exit
hot@dark/>
```

**network selection**

```
hot@dark/> network use
Network(s) found:
    1 - ark
    2 - dark
Choose an item: [1-2]> 1
hot@ark/network>
```

**advanced network commmand**

```
hot@dark/> network use ark -b 6 -s http://107.191.62.63:4001 -l 500
```

use `ark` network with `http://107.191.62.63:4001` as api entry point and 6 broadcasting-peers with latency <= `500` ms

```
hot@ark/network> ping
           http://5.39.9.242:4001: 0.031231
       http://173.253.129.20:4001: 0.375045
         http://193.70.72.90:4001: 0.031247
    >>> http://107.191.62.63:4001: 0.390701
           http://5.39.9.251:4001: 0.03136
         http://193.70.72.89:4001: 0.046769
       http://217.182.69.250:4001: 0.046836
```

From network you can get some basic informations.

```
hot@ark/network> address "secret with space between double quotes"
    APKQMy6jHF97Ur5osFw74qfid4GLfDJ8JL
hot@ark/network> publickey "secret with space between double quotes"
    02245c91ed853aa4b529c35382e2404e826cb52f0a251c3cb8b7ad2ea651acb008
hot@ark/network> use dark
hot@dark/network> address "secret with space between double quotes"
    DCgdFjBkFWPFCt4R3CGLTiaE2b4wja4AoL
hot@dark/network> delegates
    darkjarunik : 115002804.399
    d_arky      : 9821029.800
    d_chris     : 44773.053
    drafty      : 44299.200
    dravelou    : 21066.253
    cyrus19901  : 9974.000
    genesis_34  : 9898.900
    gr33ndrag0n : 8705.300
    hiddendevnet: 5029.529
    kiashaan    : 4927.800
    d_chris2    : 4303.647
    rajani      : 74.000
    genesis_22  : 0.000
    genesis_36  : 0.000
    genesis_14  : 0.000
    genesis_31  : 0.000
    genesis_48  : 0.000
    boldninja   : 0.000
    genesis_44  : 0.000
    genesis_21  : 0.000
    genesis_6   : 0.000
    genesis_23  : 0.000
    genesis_28  : 0.000
    genesis_24  : 0.000
    genesis_11  : 0.000
    genesis_32  : 0.000
    genesis_8   : 0.000
    genesis_47  : 0.000
    genesis_35  : 0.000
    genesis_16  : 0.000
    dark_jmc    : 0.000
    d_chris1    : 0.000
    genesis_7   : 0.000
    arkvader    : 0.000
    genesis_50  : 0.000
    genesis_30  : 0.000
    genesis_27  : 0.000
    genesis_3   : 0.000
    genesis_2   : 0.000
    genesis_33  : 0.000
    genesis_13  : 0.000
    genesis_19  : 0.000
    genesis_39  : 0.000
    genesis_25  : 0.000
    genesis_26  : 0.000
    genesis_5   : 0.000
    genesis_46  : 0.000
    genesis_37  : 0.000
    genesis_41  : 0.000
    genesis_20  : 0.000
    genesis_40  : 0.000
hot@dark/network>
```
