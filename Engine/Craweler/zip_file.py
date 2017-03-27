#!/usr/bin/env python
#-*- coding: utf8 -*-

import os
import zipfile

def zip_files(src, dst):
	# zip file within current dir if dir empty not zip
	with zipfile.ZipFile("%s.zip" % (dst), "w") as zf:
		abs_src = os.path.abspath(src)
		for dirname, subdirs, files in os.walk(src):
			for filename in files:
				absname = os.path.abspath(os.path.join(dirname, filename))
				arcname = absname[len(abs_src) + 1:]
				print 'zipping %s as %s' % (os.path.join(dirname, filename), arcname)
				zf.write(absname, arcname)
