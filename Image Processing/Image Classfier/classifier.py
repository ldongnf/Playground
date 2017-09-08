from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.externals import joblib
from sklearn import svm

import numpy as np
import argparse
import random

import cv2
import os

IMG_SUFFIX = ["png", "jpg", "jpeg", "bmp"]

class Classifier:
	# feature extractor type
	COLOR_HISTOGRAM = 0
	# classifier model
	KNN_CLASSIFIER = 0
	SVM_CLASSIFIER = 1

	def __init__(self, dataset_path="./train"):
		# dataset_path: dataset_path
		self.dataset_path = dataset_path

		self.model_path = None
		self.model = None

	def init_model(self, classifier_type=KNN_CLASSIFIER, rebuild=False, **options):
		# classifier_type = KNN
		# rebuid: whether to rebuild the model
		# *args: trailing argument
		# *options: dictionary variable

		self.model_path = './model/%s_%d.pkl' % (self.dataset_path.split('/')[-1], classifier_type)
		
		if classifier_type == Classifier.KNN_CLASSIFIER:
			neighbors = options.get("neighbors", 1)
			jobs = options.get("jobs", -1)
			self.model = KNeighborsClassifier(n_neighbors=neighbors, n_jobs=jobs)
			print "Model inited: KNN_Model, neighbors: %d, jobs: %d" % (neighbors, jobs)

		elif classifier_type == Classifier.SVM_CLASSIFIER:
			gamma = options.get("gamma", 0.001)
			self.model = svm.SVC(gamma=gamma)
			print "Model inited: SVM_Model, gamma: %.3f" % (gamma)

		if os.path.exists(self.model_path) and not rebuild:
			self.load_model()
		else:
			test_size = options.get("test_size", 0.25)
			self.rebuild_model(test_size=test_size)

		
	def rebuild_model(self, test_size=0.25, random_state=42):
		# test_size: what portion did the test smaples have
		# random_state: random choose the samples
		
		labels, features = self.generate_label_feature()

		labels = np.array(labels)
		features = np.array(features)
		
		(train_features, test_features, train_labels, test_labels) = train_test_split(features, labels, test_size=test_size, random_state=random_state)

		self.train_model(train_labels, train_features)
		self.save_model()
		self.test_model(test_labels, test_features)
		
	def save_model(self):
		joblib.dump(self.model, self.model_path)

	def load_model(self):
		self.model = joblib.load(self.model_path)

	def train_model(self, labels, features):
		print "Number of Train Smaples: %d" % len(labels)
		self.model.fit(features, labels)

	def test_model(self, labels, features):
		# labels: test_labels
		# features: features

		labels = np.array(labels)
		features = np.array(features)
		
		acc = self.model.score(features, labels)
		print("Model Accuracy: {:.2f}%".format(acc * 100))

	def predict(self, image_pathes):
		# image_pathes: source image path

		result = []
		for image_path in image_pathes:
			image = cv2.imread(image_path)
			raw_img_feature = self.extract_feature(image)
			img_feature = np.array([raw_img_feature])
			label = self.model.predict(img_feature)[0]
			result.append((image_path, label))
		return result

	def extract_feature(self, image, methods=COLOR_HISTOGRAM):
		# image: cv2 image object
		# methods: method to extract feature

		if methods == Classifier.COLOR_HISTOGRAM:
			return self.extract_color_histogram(image)

	def extract_color_histogram(self, image, bins=(8, 8, 8)):
		# image: cv2 image object
		# bins: channels
		# rtype: histogram

		hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
		hist = cv2.calcHist([hsv], [0, 1, 2], None, bins, [0, 180, 0, 256, 0, 256])
		hist = cv2.normalize(hist, hist).flatten()
		return hist 

	def generate_label_feature(self, dataset_path=None):
		# dataset_path: dataset_path
		# rtype: label : tuple label feature

		if not dataset_path:
			dataset_path = self.dataset_path

		label_features_dict = {}
		labels, features = [], []

		image_pathes = [dataset_path + '/' + direct for direct in os.listdir(dataset_path) if direct.endswith(tuple(IMG_SUFFIX))]
		for index, path in enumerate(image_pathes):
			image = cv2.imread(path)
			label = path.split('/')[-1].split('.')[0]
			img_feature = self.extract_feature(image)
			
			labels.append(label)
			features.append(img_feature)

			if index > 0 and index % 1000 == 0:
				print("[INFO] processed {}/{}".format(index, len(image_pathes)))

		return [labels, features]

clf = Classifier()
clf.init_model(classifier_type=Classifier.KNN_CLASSIFIER, test_size=0.01)
# model test
# [labels, features] = clf.generate_label_feature("./tests")
# clf.test_model(labels, features)

# predict
predict_dataset_path = "./dog"
image_pathes = [predict_dataset_path + '/' + direct for direct in os.listdir(predict_dataset_path) if direct.endswith(tuple(IMG_SUFFIX))]
results = clf.predict(image_pathes)
dog_count = 0
for result in results:
	if result[1] == 'dog':
		dog_count += 1
dog_total = len(results)

predict_dataset_path = "./cat"
image_pathes = [predict_dataset_path + '/' + direct for direct in os.listdir(predict_dataset_path) if direct.endswith(tuple(IMG_SUFFIX))]
results = clf.predict(image_pathes)
cat_count = 0
for result in results:
	if result[1] == 'cat':
		cat_count += 1
cat_total = len(results)

print "dog_count: %d, result: %d" % (dog_count, dog_total)
print "dog_accuracy: %.4f" % (dog_count * 1.0 / dog_total)
print "cat_count: %d, result: %d" % (cat_count, cat_total)
print "cat_accuracy: %.4f" % (cat_count * 1.0 / cat_total)
print
total_total = cat_total + dog_total
total_count = cat_count + dog_count
print "total_count: %d, result: %d" % (total_count, total_total)
print "total_accuracy: %.4f" % (total_count * 1.0 / total_total)



