#!/usr/bin/env python
# -*- coding: utf8 -*-
from datetime import datetime, timedelta
from Crypto.Cipher import AES
import hashlib
import base64

DEFAULT_KEY = "passw@rd"
LENGTH_LIMIT = 16

def encrypt_timestamp(sourcefile, resfile, days):
	# encrypt the file with tag of required time

	days_from_now = datetime.now() + timedelta(days)
	with open(sourcefile, "rb") as sfile:
		msg_text = sfile.read()
	
	msg_text += str(days_from_now.date())
	msg_text = msg_text.rjust(LENGTH_LIMIT * ((len(msg_text) / LENGTH_LIMIT) + 1))

	cipher = AES.new(DEFAULT_KEY.rjust(32), AES.MODE_ECB)
	
	encoded = base64.b64encode(cipher.encrypt(msg_text))
	
	with open(resfile, "wb") as rfile:
		rfile.write(encoded)

def decrypt_timestamp(sourcefile, resfile):
	# check whether current time is exceed the required time

	time_now = datetime.now()
	cipher = AES.new(DEFAULT_KEY.rjust(32), AES.MODE_ECB)

	with open(sourcefile, "rb") as file:
		cipher_text = file.read()

	decoded = cipher.decrypt(base64.b64decode(cipher_text)).strip()
	request_time = datetime.strptime(decoded[-10:] , '%Y-%m-%d')
	
	if time_now < request_time:
		#with open(resfile, "wb") as rfile:
		#	rfile.write(cipher_text)
		return False

	with open(resfile, "w") as rfile:
		rfile.write(decoded[:-10])
	return True

def md5(fname):
	# use md5 to compare whether the file is origin
	
	hash_md5 = hashlib.md5()
	with open(fname, "rb") as f:
		for chunk in iter(lambda: f.read(4096), b""): 
		# read method returns an empty bytes (or str, for non-binary files) at EOF
			hash_md5.update(chunk)
	return hash_md5.hexdigest()

encrypt_timestamp("source.txt", "cipher.txt", days=10)
if decrypt_timestamp("cipher.txt", "plain.txt"):
	print md5("source.txt") == md5("plain.txt")
