# Delegate with `arky`

## `hot@dark/delegate> ?`

```
Usage: delegate link [<secret> <2ndSecret>]
       delegate save <name>
       delegate unlink
       delegate status
       delegate voters
       delegate share <amount> [-c -b <blacklist> -d <delay> -l <lowest> -h <highest> <message>]

Options:
-b <blacklist> --blacklist <blacklist> ark addresses to exclude (comma-separated list or pathfile)
-h <highest> --highest <hihgest>       maximum payout in ARK
-l <lowest> --lowest <lowest>          minimum payout in ARK
-d <delay> --delay <delay>             number of fidelity-day [default: 30]
-c --complement                        share the amount complement

Subcommands:
    link   : link to delegate using secret passphrases. If secret passphrases
             contains spaces, it must be enclosed within double quotes
             ("secret with spaces"). If no secret given, it tries to link
             with saved account(s).
    save   : save linked delegate to a *.tokd file.
    unlink : unlink delegate.
    status : show information about linked delegate.
    voters : show voters contributions ([address - vote] pairs).
    share  : share ARK amount with voters (if any) according to their
             weight (1% mandatory fees). You can set a 64-char message. 
```

## `share` command for pool runners

`delegate` subsection allow user doing some basic checkings about their forging
node. A special `share` command is designed to give back voters part of forged
ark according to their vote weight.

### `<amount>`

you can specify ARK amount:
```
hot@dark/delegate[username]> share 600
Checking 30-day-true-vote-weight in transaction history...
...
```

percentage of delegate balance:
```
hot@dark/delegate[username]> share 60%
Checking 30-day-true-vote-weight in transaction history...
...
```

fiat-currency amount:
```
hot@ark/delegate[username]> share $600
$600=A716.633542 (A/$=0.837248) - Validate ? [y-n]> y
Checking 30-day-true-vote-weight in transaction history...
...
```

### --delay / -d :: True-vote-weight

To deter vote hoppers using your pool, a true-vote-weight is computed over a number of day in transaction history.

For each voter, `arky.cli` will integrate balance in ARK of the voting account over time in hours. It is actually the surface defined between balance curve and well known X-axis.

So, a 50K hopper voting on your sharing pool 12 hour before sharing happen will represent: 50,000.0 * 12 = 600,000.0 ARK.hour.
If you run a true-vote-weight:
  * over 7 days, it is equivalent to 600,000.0 / (7*24) = 3571 ARK weight vote
  * over 14 days, it is equivalent to 600,000.0 / (14*24) = 1785 ARK weight vote
  * over 30 days, it is equivalent to 600,000.0 / (30*24) = 833 ARK weight vote

### --blacklist / -b

For whatever reason you wish to ban ark account.

You can specify coma-separated ARK addresses:
```
hot@dark/delegate[username]> share 600 -b ARKADDRESS001,ARKADDRESS002,ARKADDRESS003
```

You can specify a file containing new-line-separated addresses:

```
ARKADDRESS001
ARKADDRESS002
ARKADDRESS003
```

```
hot@dark/delegate[username]> share 600 -b /path/to/file
```

### --highest / -h

You can specify a maximum payout. The cutted reward is equally-distributed to all other voters.

### --lowest / -l

You can specify a minimum payout. All voters not reaching the lowest value are excluded from the round.

### --complement / -c

Use this option if you want to send a payout round thinking about what you want to keep on your delegate account.

If you want to keep 600 ARK on your account :
```
hot@dark/delegate[username]> share 600 -c
```

If you want to keep $600 on your account :
```
hot@dark/delegate[username]> share $600 -c
```

If you want to keep 6% on your account :
```
hot@dark/delegate[username]> share 6% -c
```
