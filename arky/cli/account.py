# -*- encoding: utf8 -*-
# © Toons

'''
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
    3. a currency value using \u0024, \u00a3 or \u00a5 symbol (\u002445.6 will be converted in
       ARK using coinmarketcap API)

Usage: account link [[<secret> [<2ndSecret>]] | [-a <address>] | [-k <keyring>]]
       account save <keyring>
       account clear
       account unlink
       account status
       account balance
       account contributors
       account fidelity <days>
       account register <username>
       account register 2ndSecret <secret>
       account vote [-u <delegate>... | -d <delegate>...]
       account send <amount> <address> [<message>]
       account split <amount> <recipient>... [-m <message>]
       account share <amount> [-b <blacklist> -f <floor> -c <ceil> -s <delay> <message>]
       account support <amount> [<message>]

Options:
-u --up                                up vote all delegates name folowing
-d --down                              down vote all delegates name folowing
-b <blacklist> --blacklist <blacklist> comma-separated ark addresse list (no space)
-a <address> --address <address>       already linked ark address
-m <message> --message <message>       64-char message
-k <keyring> --keyring <keyring>       a valid *.akr pathfile
-s <delay> --strict <delay>            strict number of fidelity-day [default: 30]
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
    fidelity     : show fidelity of voters for a certain day history.
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
'''
