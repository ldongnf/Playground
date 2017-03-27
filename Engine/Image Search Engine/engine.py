# import the necessary packages
from colordescriptor import FeatureExtractor
import numpy as np
from PIL import Image
import csv
import cv2
import math
import os

IMG_SUFFIX = ["png", "jpg", "jpeg", "bmp"]

class Engine:
	def __init__(self, dataset_path="./dataset"):
		# index_path: index.csv path
		
		self.dataset_path = dataset_path
		self.index_path = "./indexes/%s_index.csv" % (self.dataset_path.split("/")[-1])
		self.feature_extractor = FeatureExtractor((8, 8, 8))

	def index_dataset(self):
		# index the dataset

		paths = [self.dataset_path + '/' + direct for direct in os.listdir(self.dataset_path) if direct.endswith(tuple(IMG_SUFFIX))]
		
		with open(self.index_path, "w") as output:
			for image_path in paths:
				print image_path
				
				image_ID = image_path.split('/')[-1]
				image = cv2.imread(image_path)
				features = self.feature_extractor.describer(image)
				features = [str(f) for f in features]

				output.write("%s,%s\n" % (image_ID, ",".join(features)))

	def chi2_distance(self, hist_A, hist_B, eps=1e-10):
		# compute the chi-squared distance
		# hist_A: histgram A
		# hist_B: histgram B
		# eps: compensate float calculate

		distance = 0.5 * np.sum([((a - b) ** 2) / (a + b + eps) for a, b in zip(hist_A, hist_B)])
		return distance

	def generate_results(self, query_img_path, num_results):
		# query_img_path: query image
		# num_results: how many results should return
		
		results = {}

		query = cv2.imread(query_img_path)
		query_features = self.feature_extractor.describer(query)

		with open(self.index_path) as file:
			reader = csv.reader(file)

			for line in reader:
				# line[0]: image ID
				# line[1:]: score feature vector
				print "compared with ", line[0]
				features = map(float, line[1:])
				distance = self.chi2_distance(features, query_features)
				results[line[0]] = distance

		# sort: more relevant images are at the front of the list
		results = sorted(results.items(), key=lambda pair:pair[1])
		return results[:num_results]

	def merge_images(self, img_paths, result_imge_width=800):
		# img_paths: imgs path
		# result_imge_width: the width of result image

		# the query img show at first line
		num_imgs = len(img_paths) - 1
		num_imgs_on_width = int(math.ceil(math.sqrt(num_imgs)))
		img_size = int(result_imge_width * 1.0 / num_imgs_on_width)
		result_image_height = int(math.ceil(num_imgs * 1.0 / num_imgs_on_width) + 1) * img_size
		
		result_img = Image.new("RGB", (result_imge_width, result_image_height), (200, 200, 200))

		img = Image.open(img_paths[0])
		img.thumbnail((img_size, img_size), Image.ANTIALIAS)
		width, height = img.size	
		result_img.paste(img, (0, 0, width, height))

		for index, path in enumerate(img_paths[1:]):
			img = Image.open(path)
			img.thumbnail((img_size, img_size), Image.ANTIALIAS)
			x = index % num_imgs_on_width * img_size
			y = (index // num_imgs_on_width + 1) * img_size
			width, height = img.size
			result_img.paste(img, (x, y, x + width, y + height))
		
		result_img.show()

	def search(self, query_img_path, num_result=5):
		# query_img_path: query_img
		# num_result: num of results
		
		if not os.path.exists(query_img_path):
			print "query image not exist"
			return

		if not os.path.exists(self.index_path):
			self.index_dataset()

		results = self.generate_results(query_img_path, num_result)
		pathes = [query_img_path] + [self.dataset_path + '/' + result_ID for result_ID, score in results]
		self.merge_images(pathes)
