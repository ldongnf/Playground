#!/usr/bin/env python
import time
import os

class Node:
	def __init__(self):
		# is_end: whther a word end in this char
		self.is_end = False
		self.children = {}

class Trie:
	def __init__(self):
		self.root = Node()

	def add(self, word):
		# word: add word to trie

		node = self.root
		for char in word:
			if char not in node.children:
				node.children[char] = Node()
			node = node.children[char]
		node.is_end = True

	def add_from_file(self, file_path):
		# add all the word in file

		with open(file_path) as file:
			words = []
			for line in file:
				words += map(str.strip, line.split())
			for word in list(set(words)):
				self.add(word)
		print file_path

	def search(self, word):
		# search a word in trie

		node = self.root
		for char in word:
			if char not in node.children:
				return False
			node = node.children[char]
		return node.is_end

	def starts_with(self, prefix):
		# search whether contain a prefix

		node = self.root
		for char in prefix:
			if char not in node.children:
				return False
			node = node.children[char]
		return True

	def to_list(self):
		# extract all the words in trie
		def traverse(root):
			# recurseve traverse the trie
			word_list = []
			for char in root.children:
				node = root.children[char]
				if node.children:
					if node.is_end:
						word_list.append(char)
					for following in traverse(node):
						word_list.append(char + following)
				else:
					word_list.append(char)
			return word_list
		return traverse(self.root)


def generate_pathes(root_dir):
	# root_dir:	root_dir
	# target_file_name:	target
	# rtype: all path from root_dir contains target
	paths = []
	for root, dirs, files in os.walk(root_dir, topdown=True):
		if not files:
			continue
		else:
			for file in files:
				profix = file.split('.')[-1]
				if profix == "txt": 
					paths.append(root + '/' + file)
	return paths


trie = Trie()
trie.add_from_file("dict.txt")
print trie.to_list()

