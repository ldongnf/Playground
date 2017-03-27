#!/usr/bin/env python
#-*- coding: utf8 -*-
"""
module_name, package_name, ClassName, 
method_name, ExceptionName, function_name, 
GLOBAL_CONSTANT_NAME, global_var_name, 
instance_var_name, function_parameter_name, 
local_var_name
"""

import random
import optparse

def generate_passphrases(num_phrases, password_for):
	dictionary = []
	with open("dictionary.txt", "r") as file:
		dictionary = [line.strip() for line in file if len(line.strip()) < 6]
	passphrases = [random.choice(dictionary) for _ in xrange(num_phrases)]

	word = random.choice(passphrases)
	passphrases.pop(passphrases.index(word))

	word = word.title()
	passphrases.insert(0, word)

	passphrases.append(random.choice([str(i) for i in xrange(10)]))
	str_passphrases = "".join(passphrases)

	with open("history.txt", "a") as f:
		f.write(password_for + ":" + str_passphrases + "\n")
	return passphrases

def commandline():
	parser = optparse.OptionParser("usage%prog "+"-n <num_phrases> -p <password_for>");
	parser.add_option('-n',dest='num_phrases',type='string',help='number of phrases');
	parser.add_option('-p',dest='password_for',type='string',help='password for what');
	(options, args) = parser.parse_args()
	if (options.num_phrases == None) or (options.password_for == None):
		print parser.usage
		exit(0)
	else:
		num_phrases = int(options.num_phrases)
		password_for = options.password_for
		passphrases = generate_passphrases(num_phrases, password_for)
		str_passphrases = "".join(passphrases)

		print passphrases
		print str_passphrases

commandline()
