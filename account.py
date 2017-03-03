# -*- encoding: utf8 -*-
# © Toons

"""
Usage: account use (<network>)
       account connect (<peer>)
       account create (<secret>)
       account open [<secret>|<address>|<wallet>]
       account status [<secret>|<address>|<wallet>]
       account register delegate (<username>)
       account register secondSecret (<secret>)
       account vote [-u <list>] [-d <list>]
       account send (<amount>) (<recipientId>) [<vendorField>]
       account save (<wallet>])
       account close

Options:
-u <list>, --up <list>   coma-separated username list to be voted up (no spaces)
-d <list>, --down <list> coma-separated username list to be voted down (no spaces)
"""
from arky import cmd 

def set_prompt(): pass
