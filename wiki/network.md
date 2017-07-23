# Network with `arky`

## `hot@dark/network> ?`

```
Usage: network use [<name> -b <number> -s <seed> -l <ms>]
       network browse [<element>]
       network publickey <secret>
       network address <secret>
       network wif <secret>
       network delegates
       network ping
       network update

Options:
-b <number> --broadcast <number> peer number to use for broadcast       [default: 10]
-s <seed> --custom-seed <seed>   custom seed you want to connect with
-l <ms> --latency <ms>           maximum latency allowed in miliseconds [default: 1000]

Subcommands:
    use       : select network.
    browse    : browse network.
    publickey : returns public key from secret.
    address   : returns address from secret.
    delegates : show delegate list.
    ping      : print selected peer latency.
    update    : update balance of all linked account.
```
