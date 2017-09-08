import numpy as np
import cv2

class FeatureExtractor:
	COLOR_DESCRIBER = 0

	def __init__(self, bins=(8, 12, 3)):
		# store the number of bins for the 3D histogram
		self.bins = bins

	def describer(self, image, describe_type=COLOR_DESCRIBER):
		if describe_type == FeatureExtractor.COLOR_DESCRIBER:
			return self.color_describer(image)

	def color_describer(self, image):
		# convert the image to the HSV color space
		# initialize the features used to quantify the image
		features = []

		image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
		
		# grab the dimensions and compute the center of the image
		h, w = image.shape[:2]
		c_X, c_Y = int(w * 0.5), int(h * 0.5)

		# divide the image into four segments
		# top-left top-right, bottom-right, bottom-left
		segments = [(0, c_X, 0, c_Y), (c_X, w, 0, c_Y), (c_X, w, c_Y, h), (0, c_X, c_Y, h)]

		# construct an mask and extract feature
		axes_X, axes_Y = int(w * 0.75) / 2, int(h * 0.75) / 2
		ellipse_mask = np.zeros(image.shape[:2], dtype = "uint8")
		cv2.ellipse(ellipse_mask, (c_X, c_Y), (axes_X, axes_Y), 0, 0, 360, 255, -1)

		for (start_X, end_X, start_Y, end_Y) in segments:
			corner_mask = np.zeros(image.shape[:2], dtype = "uint8")
			cv2.rectangle(corner_mask, (start_X, start_Y), (end_X, end_Y), 255, -1)
			corner_mask = cv2.subtract(corner_mask, ellipse_mask)

			hist = self.histogram(image, corner_mask)
			features.extend(hist)

		hist = self.histogram(image, ellipse_mask)
		features.extend(hist)

		return features

	def histogram(self, image, mask):
		# extract a 3D color histogram from the mask
		# use the supplied number of bins per channel
		# normalize the histogram

		hist = cv2.calcHist([image], [0, 1, 2], mask, self.bins, [0, 180, 0, 256, 0, 256])
		hist = cv2.normalize(hist, hist).flatten()
		return hist
