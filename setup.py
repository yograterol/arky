# -*- coding:utf-8 -*-
# created by Toons on 01/05/2017
try:
	from setuptools import setup
	import wheel
except ImportError:
	from distutils.core import setup

kw = {}

f = open("VERSION", "r")
long_description = open("readme.rst", "r")
kw.update(**{
	"version": f.read().strip(),
	"name": "Arky",
	"keywords": ["api", "ARK"],
	"author": "Toons",
	"author_email": "moustikitos@gmail.com",
	"maintainer": "Toons",
	"maintainer_email": "moustikitos@gmail.com",
	"url": "https://github.com/ArkEcosystem/arky",
	"download_url": "https://github.com/ArkEcosystem/arky.git",
	"data_files": [(".", ["arky/ark.net", "arky/dark.net"])],
	"description": "Pythonic way to work with Ark.io EcoSystem.",
	"long_description": long_description.read(),
	"packages": ["arky", "arky.api", "arky.util", "arky.cli"],
	"scripts": ["arky-cli.py"],
	"install_requires": ["requests", "ecdsa", "pytz", "base58", "docopt"],
	"license": "Copyright 2016-2017 Toons, Copyright 2017 ARK, MIT licence",
	"classifiers": [
		'Development Status :: 6 - Mature',
		'Environment :: Console',
		'Environment :: Web Environment',
		'Intended Audience :: Developers',
		'Intended Audience :: End Users/Desktop',
		'License :: OSI Approved :: MIT License',
		'Operating System :: OS Independent',
		'Programming Language :: Python',
		'Programming Language :: Python :: 2',
		'Programming Language :: Python :: 3',
	],
})
long_description.close()
f.close()

setup(**kw)
