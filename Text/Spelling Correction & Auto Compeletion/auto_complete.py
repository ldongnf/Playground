#!/usr/bin/env python
#-*- coding: utf8 -*-

"""
module_name, package_name, ClassName, method_name, 
ExceptionName, function_name, GLOBAL_CONSTANT_NAME, 
global_var_name, instance_var_name, 
function_parameter_name, local_var_name
"""

# correct the spelling error of a given word use the English
# dictionary and the frequency of commonly used word

from collections import Counter
import re
import sys

def generate_dictionary(fname):
	# generate the dictionary for word suggestion

	with open(fname, "r") as file:
		return Counter([line.strip() for line in file])

def auto_complete(prefix, suggestions):
	# current prefix of word
	# suggestions: number of words to suggest
	# counter used to indicate the frequency of word

	counter = generate_dictionary("dict.txt")
	counter_key = counter.keys()
	candidates, temp = [], []
	history = set()

	# get the words at length of current prefix
	# if still small learn than required
	# shrink the prefix
	i = len(prefix)
	while len(history) < suggestions:
		temp = [key for key in counter_key if key.startswith(prefix[:i]) if key not in history]
		temp = sorted(temp, key=lambda item:counter[item], reverse=True)
		history = set(list(history) + temp)
		if temp:
			candidates.append(temp[:])
		i -= 1

	# possibly suggestion > required
	result = []
	while len(result) < suggestions:
		for candidate in candidates:
			result += candidate[:suggestions - len(result)]
	return result

if __name__=='__main__':
	word = sys.argv[1]
	num = int(sys.argv[2])
	print auto_complete(word, num)
	
