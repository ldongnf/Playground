#!/usr/bin/env python
#-*- coding: utf8 -*-

import os
import optparse
from zipfile import *

def zip_files(src):
	# zip file within current dir if dir empty not zip
	with ZipFile("%s.zip" % (src), "w") as zf:
		abs_src = os.path.abspath(src)
		for dirname, subdirs, files in os.walk(src):
			for filename in files:
				absname = os.path.abspath(os.path.join(dirname, filename))
				arcname = absname[len(abs_src) + 1:]
				print 'zipping %s as %s' % (os.path.join(dirname, filename), arcname)
				zf.write(absname, arcname)

def brute_force_zip(fname, pwdname):
	# read the keyword store in the file
	# brute force try each pwd

	with open(pwdname, "r") as f:
		passwords = [line.strip() for line in f]

	des_dir = fname[:-4]
	with ZipFile(fname) as zf:
		for password in passwords:
			try:
				zf.extractall(des_dir, pwd=password)
				print("PASSWORD IS:"+password)
				exit(0)
			except Exception as e:
				pass
	os.rmdir("./"+fname)

def commandline():
	# the command line
	parser = optparse.OptionParser("usage%prog "+"-t <type> -f <zipfile> -d <dictFile>");
	parser.add_option('-t',dest='zip_type',type='string',help='type');
	parser.add_option('-f',dest='fname',type='string',help='specify zip file');
	parser.add_option('-d',dest='pwdname',type='string',help='specify possible pwd file');
	(options, args) = parser.parse_args()
	if options.zip_type == None:
		print parser.usage
		exit(0)
	else:
		zip_type = options.zip_type
		if zip_type == "zip":
			if options.fname == None:
				print parser.usage
				exit(0)
			fname = options.fname
			zip_files(fname)
		if zip_type == "unzip":
			if (options.fname == None) or (options.pwdname == None):
				print parser.usage
				exit(0)
			fname = options.fname
			pwdname = options.pwdname
			brute_force_zip(fname, pwdname)

commandline()

