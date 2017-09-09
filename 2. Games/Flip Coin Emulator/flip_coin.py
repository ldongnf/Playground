import matplotlib as mil 
mil.use('TkAgg')
import matplotlib.pyplot as plt

import random
import numpy as np
from threading import Thread
from Queue import *
import time
import os
import sys

HEAD = 0
TAIL = 1

class Worker(Thread):
	def __init__(self, tasks):
		Thread.__init__(self)
		self.tasks = tasks
		self.daemon = True
		self.start()

	def run(self):
		while True:
			func, args, kargs = self.tasks.get()
			try:
				func(*args, **kargs)
				#print self.name, self.ident
				time.sleep(.1)
			except Exception as e:
				# An exception happened in this thread
				print(e)
			finally:
				# Mark this task as done, whether an exception happened or not
				self.tasks.task_done()

class ThreadPool:
	""" Pool of threads consuming tasks from a queue """
	def __init__(self, num_threads):
		self.tasks = Queue(num_threads)
		self.workers = [Worker(self.tasks) for _ in range(num_threads)]

	def add_task(self, func, *args, **kargs):
		""" Add a task to the queue """
		self.tasks.put((func, args, kargs))

	def map(self, func, args_list):
		""" Add a list of tasks to the queue """
		for args in args_list:
			self.add_task(func, *args)

	def wait_completion(self):
		""" Wait for completion of all the tasks in the queue """
		self.tasks.join()

def flip_coins(experiment_times, filp_times):
	with open("./result.txt", 'a') as file:
		for i in xrange(experiment_times):	
			head_count = sum([random.choice([HEAD, TAIL]) for _ in xrange(filp_times)])
			probability = 1.0 * head_count / filp_times
			print "head: %d, tail: %d, prob:%.4f" % (head_count, filp_times - head_count, probability)
			file.write("%.4f\n" % probability)

def generate_result():
	with open("./result.txt", 'r') as file:
		x, y = [], []
		for index, line in enumerate(file):
			probability = line.rstrip()
			x.append(index)
			y.append(probability)

	plt.scatter(x, y)
	plt.xlabel('Experiments')
	plt.ylabel('Probability')
	plt.title('Coin Emulation')
	plt.show()

def dispatch(experiment_times=10000, filp_times=10000, workers=100):
	while experiment_times / workers <= 0:
		workers /= 10

	start = time.time()
	if os.path.exists("./result.txt"):
		os.remove("./result.txt")
	pool = ThreadPool(workers)
	pool.map(flip_coins, [(experiment_times / workers, filp_times) for _ in xrange(workers)])
	pool.wait_completion()
	print time.time() - start
	generate_result()

experiment_times = 10000
filp_times = 10000

try:
	experiment_times = int(sys.argv[1])
except:
	pass
try:
	filp_times = int(sys.argv[2])
except:
	pass

dispatch(experiment_times, filp_times)

