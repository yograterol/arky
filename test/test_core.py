import doctest, binascii
import arky.core

arky.core.use("testnet")
doctest.testmod(arky.core)
