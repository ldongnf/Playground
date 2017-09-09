#!/usr/bin/env python
#-*- coding: utf8 -*-

"""
module_name, package_name, ClassName, method_name, 
ExceptionName, function_name, GLOBAL_CONSTANT_NAME, 
global_var_name, instance_var_name, 
function_parameter_name, local_var_name
"""

# used to learn mutliple thread in python

from threading import Thread
from Queue import *
import time

import itertools
from operator import itemgetter
from rarfile import *
import os
import random

class Task:
	# task class

	def __init__(self, func, *args, **kargs):
		# func: function

		self.func = func
		self.args = args
		self.kargs = kargs

	def run(self):
		# run the fuction

		self.func(*self.args, **self.kargs)

	def show_info(self):
		# print infomation about this task

		print "functiona", self.func
		print "args"
		for arg in self.args:
			print arg
		print "kargs"
		for key,value in self.kargs.iteritems():
			print key, "=", value

class Worker(Thread):
	def __init__(self, id, name, tasks):
		Thread.__init__(self)
		self.tasks = tasks
		self.daemon = True
		self.id = id
		self.name = name
		self.start()

	def run(self):
		while True:
			task = self.tasks.get()
			try:
				print "Thread: %d, name: %s is working\n" % (self.id, self.name),
				task.run()
				time.sleep(.1)
			except Exception as e:
				print e
			finally:
				print "Thread: %d, name: %s is Done\n" % (self.id, self.name),
				self.tasks.task_done()

class Master:
	def __init__(self, num_threads=5):
		self.tasks = Queue()
		self.workers = [Worker(i, "Worker %d"%i, self.tasks) for i in range(num_threads)]

	def add_task(self, func, *args, **kargs):
		self.tasks.put(Task(func, *args, **kargs))

	def map(self, task_list):
		for (func, args, kargs) in task_list:
			self.add_task(func, *args, **kargs)

	def run(self):
		self.tasks.join()

def brute_force_try(rar_path, work_id, passwords):
	with RarFile(rar_path) as zf:
		directary = "/".join(rar_path.split('/')[:-1])
		for index, password in enumerate(passwords):
			if index % 10 == 0:
				print "Thread %d has completed %d" % (work_id, index)
			if index % (100 + work_id) == 0:
				print "Thread %d has completed %d" % (work_id, index)
				backup("./temp/temp_%d_%d.txt"%(work_id, len(passwords[index:])), passwords[index:])
			if os.path.exists("./temp/password.txt"):
				break
			try:
				zf.extractall(directary, pwd=password)
				with open("./temp/password.txt", "w") as password_file:
					print("PASSWORD IS:" + password)
					password_file.write(password)
				break
			except:
				pass
		try:
			os.rmdir(directary)
		except:
			pass

def backup(filename, datas):
	with open(filename, "w") as file:
		for line in datas:
			file.write(line + "\n")
		file.close()

def generate_passwords_file(directary="./temp", password_file_name="./1.txt", password_len=4):
	SUFFIX = ['txt']
	if os.path.exists(directary):
		# all the files in the directary
		files = [file for file in os.listdir(directary) if file.endswith(tuple(SUFFIX))]
		file_names = [file.split('.')[0].split('_') for file in files]

		dictionary = {}
		for letter, words in itertools.groupby(sorted(file_names), key=itemgetter(1)):
			dictionary[letter] = "_".join(min(words, key=lambda item:int(item[2]))) + ".txt"
		recent_files = dictionary.values()

		print recent_files

		with open(password_file_name, "w") as file:
			for seg_file in recent_files:
				with open(directary+'/'+seg_file, "r") as input_file:
					file.write(input_file.read())
		
		for file in files:
			if os.path.exists(directary+'/'+file):
				os.remove(directary+'/'+file)
	else:
		os.mkdir(directary)
		letters = "qwertyuioplkjhgfdsazxcvbnm"
		passwords = map(''.join, list(itertools.product(letters, repeat=password_len)))

		with open(password_file_name, "w") as file:
			for line in passwords:
				file.write(line+'\n')

generate_passwords_file()

with open('1.txt', "r") as f:
	passwords = [line.strip() for line in f]
random.shuffle(passwords)

num_threads = 80
print len(passwords)
seg_length = len(passwords) / num_threads

master = Master(num_threads)
task_list = [(brute_force_try, ("./2.rar", i, passwords[i*seg_length : (i+1)*seg_length]), {}) for i in xrange(100)]

master.map(task_list)
master.run()

