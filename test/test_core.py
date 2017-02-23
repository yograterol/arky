from arky import __PY3__
import doctest, binascii
import arky.core

if not __PY3__:
	raise Exception("doctest is written for python 3.x familly")

arky.core.api.use("testnet")
doctest.testmod(arky.core)
