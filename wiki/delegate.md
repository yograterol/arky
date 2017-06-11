# Delegate with `arky`

## `hot@dark/delegate> ?`

```
Usage: delegate link [<secret>]
       delegate save <name>
       delegate unlink
       delegate status
       delegate voters
       delegate share <amount> [-c -b <blacklist> -d <delay> <message>]

Options:
-b <blacklist> --blacklist <blacklist> comma-separated ark addresses to exclude
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
             weight. You can set a 64-char message.
```
