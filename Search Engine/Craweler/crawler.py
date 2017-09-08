#!/usr/bin/env python
#-*- coding: utf8 -*-
"""
module_name, package_name, ClassName, 
method_name, ExceptionName, function_name, 
GLOBAL_CONSTANT_NAME, global_var_name, 
instance_var_name, function_parameter_name, 
local_var_name
"""

from Queue import *
from urllib import *
from urlparse import urlparse
from bs4 import BeautifulSoup
from threading import Thread
import requests
import time
import datetime
#from zip_file import zip_files

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
			self.add_task(func, args)

	def wait_completion(self):
		""" Wait for completion of all the tasks in the queue """
		self.tasks.join()

class Crawler(object):
	# variable shared with all instance
	IMG_SIZE_LIMIT = 1024 * 2
	FILE_SIZE_LIMIT = 1024
	IMG_TYPE = ['jpg', 'png', 'jpeg', 'svg']#'gif'
	OUTPUT_CHUCK_SIZE = 1024
	HISTORY_SIZE_LIMIT = 2048
	DISPATCH_COEFFICENT = 10

	# Crawler Type
	CRAWLER_DEFAULT = 0
	CRAWLER_IMG = 1
	
	def __init__(self, root_url, max_depth=1, max_download=100, max_workers=5):
		self.root_url = root_url
		self.max_depth = max_depth
		self.max_download = max_download
		self.max_workers = max_workers

		self.url_queue = Queue()
		self.url_queue_buffer = Queue()
		self.url_queue.put(self.root_url)
		
		self.url_history = set()
		self.url_history.add(self.root_url)
	
		self.data_buffer = Queue()
		self.data_history = set()
		self.count = 0

		self.workers_pool = ThreadPool(max_workers * Crawler.DISPATCH_COEFFICENT)

	def run(self, crawler_type=CRAWLER_DEFAULT, download = True, store_path = "htm", focus = True):
		if download:
			while self.count < self.max_download and self.max_depth >= 0 and not self.url_queue.empty():			
				self.dispatcher(crawler_type, download, store_path)
				#self.need_backup("data")
				#self.single_dispatcher(crawler_type, download, store_path)
				
			print self.count, self.max_depth, self.url_queue.qsize()
		else:
			while len(self.url_history) < self.max_download and self.max_depth >= 0 and not self.url_queue.empty():			
				self.dispatcher(crawler_type, download, store_path)
			self.save_links("./backup/url_res.txt", "url")
			print len(self.url_history)
		#zip_files(save_dir, "test")

	def dispatcher(self, crawler_type=CRAWLER_DEFAULT, download = True, store_path = "htm"):
		self.workers_pool.map(self.parser, [crawler_type for _ in xrange(self.max_workers)])
		if download:
			work_remains = self.max_download - self.count
			work_remains = min(work_remains, Crawler.DISPATCH_COEFFICENT * self.max_workers)
			if crawler_type == Crawler.CRAWLER_DEFAULT:
				self.workers_pool.map(self.download_html_file, [store_path for _ in xrange(work_remains)])
			if crawler_type == Crawler.CRAWLER_IMG:
				self.workers_pool.map(self.download_data, [store_path for _ in xrange(work_remains)])
		self.workers_pool.wait_completion()

	def single_dispatcher(self, crawler_type=CRAWLER_DEFAULT, download = True, store_path = "htm"):
		self.workers_pool.map(self.parser, [crawler_type])
		if download:
			work_remains = self.max_download - self.count
			work_remains = min(work_remains, Crawler.DISPATCH_COEFFICENT * self.max_workers)
			if crawler_type == Crawler.CRAWLER_DEFAULT:
				self.workers_pool.map(self.download_html_file, [store_path])
			if crawler_type == Crawler.CRAWLER_IMG:
				self.workers_pool.map(self.download_data, [store_path])
		self.workers_pool.wait_completion()

	def parser(self, crawler_type=CRAWLER_DEFAULT, focus=True):
		if self.url_queue.empty():
			return
		
		try:
			url = self.url_queue.get(True, .1)
		except:
			return 

		try:
			html = urlopen(url).read()
		except Exception as e:
			self.log(e, url)
			return

		soup = BeautifulSoup(html, "html.parser")
		self.extract_url(soup, url, focus)

		if crawler_type == Crawler.CRAWLER_DEFAULT:
			if url not in self.data_history:
				self.data_buffer.put(url)
				self.data_history.add(url)

		if crawler_type == Crawler.CRAWLER_IMG:
			self.extarct_data(soup, url, "img", "src")

	def extract_url(self, soup, url, focus=True):
		links = [href.get("href") for href in soup.find_all('a', href=True)]
		if focus:
			for link in links:
				new_url = self.validate_url(link, url)
				if new_url.startswith(self.root_url):
					if new_url not in self.url_history:
						if self.url_queue.empty():
							self.max_depth -= 1
							print  "depth", self.max_depth
							self.url_queue, self.url_queue_buffer = self.url_queue_buffer, self.url_queue
						self.url_queue_buffer.put(new_url)
						self.url_history.add(new_url)
		else:
			for link in links:
				new_url = self.validate_url(link, url)
				if new_url not in self.url_history:
					if self.url_queue.empty():
						self.url_queue, self.url_queue_buffer = self.url_queue_buffer, self.url_queue
					self.url_queue_buffer.put(new_url)
					self.url_history.add(new_url)	
	
	def extarct_data(self, soup, url, tag, attr):
		result = soup.find_all(tag)
		if result:
			links = [link.get(attr) for link in result if link.get(attr)]
			for link in links:
				new_url = self.validate_url(link, url)
				if new_url[-3:] in Crawler.IMG_TYPE and new_url not in self.data_history:
					self.data_buffer.put(new_url)
					self.data_history.add(new_url)

	def validate_url(self, target, root_url):
		url_parse_res = urlparse(target)
		new_url = target.split("#" , 1)[0]
		if not url_parse_res.scheme:
			if url_parse_res.netloc:
				new_url = '{uri.scheme}:'.format(uri=urlparse(root_url)) + new_url
			else:
				if not new_url.startswith('/'):
					new_url = '/' + new_url
				new_url = '{uri.scheme}://{uri.netloc}'.format(uri=urlparse(root_url)) + new_url
		return new_url
	
	def download_data(self, directory):
		if self.data_buffer.empty():
			return
		try:
			url = self.data_buffer.get(True, .1)
		except:
			return

		file_name = url.split('/')[-1]
		response = requests.get(url, stream=True)
		
		if not response.ok:
			print response
			return

		if len(response.content) <= Crawler.IMG_SIZE_LIMIT:
			print "File Too Small"
			return

		print "No: ", self.count
		print

		with open(directory + '/' + file_name, 'wb') as handle:
			for block in response.iter_content(Crawler.OUTPUT_CHUCK_SIZE):
				if not block:
					break
				handle.write(block)
		self.count += 1
			
	def download_html_file(self, directory):
		if self.data_buffer.empty():
			return
		url = self.data_buffer.get()

		try:
			html = urlopen(url).read()
		except Exception as e:
			self.log(e, url)
			return
		
		print url
		
		if len(html) <= Crawler.FILE_SIZE_LIMIT:
			print "File Too Small"
			return

		soup = BeautifulSoup(html, "html.parser")
		result = soup.find('body').get_text()
		with open("./" + directory + "/%s.txt" % soup.title.string, "w") as file:
			file.write(result.encode('utf8'))
		#with open("./" + directory + "/%s.html" % soup.title.string, "w") as file:
		#	file.write(html)
				
		print "No: ", self.count
		print
		
		self.count += 1
		
	def save_links(self, path, history_name):
		data = None
		if history_name == "url":
			data = self.url_history
		if history_name == "data":
			data = self.data_history
		if not data:
			return
		with open(path, "w") as file:
			for link in data:
				try:
					file.write(link+'\n')
				except Exception as e:
					try:
						mystring = link.encode('UTF-8')
						file.write(mystring+'\n')
					except Exception as exc:
						self.log(exc, link)

	def log(self, exception, *args, **kargs):
		print "----------------"
		for arg in args:
			print arg
		for key in kargs:
			print key, kargs[key]
		print exception
		print "----------------"
		print

	def need_backup(self, history_name="url"):
		full_data = []
		if history_name == "url":
			if len(self.url_history) > Crawler.HISTORY_SIZE_LIMIT:
				full_data = list(self.url_history)
				self.url_history = set(full_data[Crawler.HISTORY_SIZE_LIMIT:])
		if history_name == "data":
			if len(self.data_history) > Crawler.HISTORY_SIZE_LIMIT:
				full_data = list(self.data_history)
				self.data_history = set(full_data[Crawler.HISTORY_SIZE_LIMIT:])
		if full_data:
			file_name = str(datetime.datetime.now())
			with open("./backup/%s/%s.txt" % (history_name, file_name), "w") as file:
				for data in full_data[:Crawler.HISTORY_SIZE_LIMIT]:
					file.write(data + '\n')
		print
		print "---------------"
		print len(self.url_history), len(self.data_history)
		print "---------------"
		print
			
def main():
	url = "http://www.cnn.com/"
	max_download = 1000
	max_workers = 20
	max_depth = 6
	my_crawler = Crawler(url, max_depth, max_download, max_workers)
	start_time = time.time()
	#my_crawler.run(Crawler.CRAWLER_IMG, True, "../img")
	my_crawler.run(Crawler.CRAWLER_DEFAULT, True, "htm")
	end_time = time.time()
	
	print "Operating Time: %s" % (end_time - start_time)

if __name__== "__main__":
	main()
