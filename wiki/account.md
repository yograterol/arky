# Account with `arky`

## `hot@dark/account> ?`

```
Usage: account link [<secret>]
       account save <name>
       account unlink
       account status
       account register <username>
       account register 2ndSecret <secret>
       account vote [-u <delegate> | -d <delegate>]
       account send <amount> <address> [<message>]

Options:
-u --up   up vote all delegate name folowing
-d --down down vote all delegate name folowing

Subcommands:
    link     : link to account using secret passphrases. If secret passphrases
               contains spaces, it must be enclosed within double quotes
               ("secret with spaces"). If no secret given, it tries to link
               with saved account(s).
    save     : save linked account to a *.tok file.
    unlink   : unlink account.
    status   : show information about linked account.
    register : register linked account as delegate (cost 25 ARK);
               or
               register second signature to linked account (cost 5 ARK).
    vote     : up or down vote delegate.
    send     : send ARK amount to address. You can set a 64-char message.
```
