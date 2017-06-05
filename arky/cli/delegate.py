# -*- encoding: utf8 -*-
# © Toons

'''
Usage: account link [<secret>]
       account save <name>
       account unlink
       account status
       account contributors
       account fidelity <days>
       account share <amount> [-b <blacklist> -s <delay> <message>]
       account support <amount> [<message>]

Options:
-b <blacklist> --blacklist <blacklist> comma-separated ark addresse list (no space)
-a <address> --address <address>       already linked ark address
-k <keyring> --keyring <keyring>       a valid *.akr pathfile
-s <delay> --strict <delay>            strict number of fidelity-day [default: 30]

Subcommands:
    link         : link to account using secret passphrases, Ark address or
                   *.akr file. If secret passphrases contains spaces, it must be
                   enclosed within double quotes ("secret with spaces"). Note
                   that you can use address only for *.akr files registered
                   locally.
    save         : save linked account to an *.akr file.
    unlink       : unlink account and delete its associated *.akr file.
    status       : show information about linked account.
    contributors : show voters contributions ([address - vote weight] pairs).
    fidelity     : show fidelity of voters for a certain day history.
    share        : share ARK amount with voters (if any) according to their
                   weight. You can set a 64-char message.
    support      : share ARK amount to relay nodes according to their vote rate.
                   You can set a 64-char message.
'''
