# -*- encoding: utf8 -*-
# © Toons

from . import ArkyDict, __PY3__

# Global containers available for arky package
__EXPLORER__ = False
__TOKEN__ = False
__SYMBOL__ = False
__HOT_MODE__ = False
__BEGIN_TIME__ = 0
__NET__ = "..."
__NETWORK__ = ArkyDict()
__HEADERS__ = ArkyDict()

# ARK fees according to transactions in SATOSHI
__FEES__ = ArkyDict({
	"send": 10000000,
	"vote": 100000000,
	"delegate": 2500000000,
	"secondsignature": 500000000,
	"multisignature": 500000000,
	"dapp": 2500000000
})
