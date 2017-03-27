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
	# word frequency
	with open(fname, "r") as file:
		return Counter([line.strip() for line in file])

def words_edit_distance_1(word):
	# modify the word with one edit distance
	# modification include:
	# delete a char
	# swap two char
	# replace a char
	# insert a char

	letters = "abcdefghijklmnopqrstuvwxyz"
	splits = [(word[:i], word[i:]) for i in xrange(len(word) + 1)]
	delete = [left + right[1:] for left, right in splits if right]
	transpose = [left + right[1] + right[0] + right[2:] for left, right in splits if len(right) > 1]
	replace = [left + char + right[1:] for left, right in splits for char in letters if right]
	insert = [left + char + right for left, right in splits for char in letters]
	return set(delete + transpose + replace + insert)

def words_edit_distance_2(word): 
	# word with modification at distance 2
	return set(e2 for e1 in words_edit_distance_1(word) for e2 in words_edit_distance_1(e1))

def filter_words(dictionary, words):
	# filter the word not in frequency dictionary
	return [word for word in words if word in dictionary]

def get_all_possible_words(dictionary, word):
	# return word cadidate
	all_possible_words = set(list(words_edit_distance_1(word)) + list(words_edit_distance_2(word)) + [word])
	return filter_words(dictionary, all_possible_words)

def correction(word, num_correctin):
	# return suggestion correction according to the frequency
	dictionary = generate_dictionary('dict.txt')
	candidates = get_all_possible_words(dictionary, word)
	candidates_with_frequency = sorted([(key, dictionary[key]) for key in candidates], key=lambda item : item[1], reverse=True)
	result = [item[0] for item in candidates_with_frequency]
	return result[:num_correctin] if word not in result else word

if __name__=='__main__':
	word, num = sys.argv[1], int(sys.argv[2])
	sys.exit(correction(word, num))
	
