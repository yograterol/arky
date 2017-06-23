# Delegate with `arky`

## `hot@dark/delegate> ?`

```
Usage: delegate link [<secret>]
       delegate save <name>
       delegate unlink
       delegate status
       delegate voters
       delegate share <amount> [-c -b <blacklist> -d <delay> -l <lowest> -h <highest> <message>]

Options:
-b <blacklist> --blacklist <blacklist> comma-separated line or file containing ark addresses to exclude
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
hot@dark/delegate[arky]> share 600
Checking 30-day-true-vote-weight in transaction history...
...
```

percentage of delegate balance:
```
hot@dark/delegate[arky]> share 60%
Checking 30-day-true-vote-weight in transaction history...
...
```

fiat-currency amount:
```
hot@ark/delegate[arky]> share $600
$600=A716.633542 (A/$=0.837248) - Validate ? [y-n]> y
Checking 30-day-true-vote-weight in transaction history...
...
```

### True-vote-weight ?


### --blacklist / -b


### 
