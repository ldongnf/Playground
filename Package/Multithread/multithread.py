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


class Task:
	# task class

	def __init__(self, func, *args, **kwargs):
		# func: function

		self.func = func
		self.args = args
		self.kwargs = kwargs

	def run(self):
		# run the fuction

		self.func(*self.args, **self.kwargs)

	def show_info(self):
		# print infomation about this task

		print "functiona", self.func
		print "args"
		for arg in self.args:
			print arg
		print "kwargs"
		for key, value in self.kwargs.iteritems():
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

	def add_task(self, func, *args, **kwargs):
		self.tasks.put(Task(func, *args, **kwargs))

	def map(self, task_list):
		for (func, args, kwargs) in task_list:
			self.add_task(func, *args, **kwargs)

	def run(self):
		self.tasks.join()