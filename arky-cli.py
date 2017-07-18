# -*- coding:utf-8 -*-
# created by Toons on 01/05/2017

from arky import cli
from arky import api
import io, os, sys

if __name__ == "__main__":
	if len(sys.argv) > 1 and os.path.exists(sys.argv[-1]):
		cli.launch(sys.argv[-1])
	else:
		cli.start()
