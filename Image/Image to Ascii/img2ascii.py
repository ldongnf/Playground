#!/usr/bin/env python
#-*- coding: utf8 -*-

"""
module_name, package_name, ClassName, method_name, 
ExceptionName, function_name, GLOBAL_CONSTANT_NAME, 
global_var_name, instance_var_name, 
function_parameter_name, local_var_name
"""

from PIL import Image
import sys

# output char
ASCII_CHARS = [ '#', '?', '%', '.', 'S', '+', '.', '*', ':', ',', '@']

def scale_image(image, new_width=150):
	# scale image to new width by ratio
	(original_width, original_height) = image.size
	aspect_ratio = new_width/float(original_width)
	new_height = int(aspect_ratio * original_height)
	new_image = image.resize((new_width, new_height))
	return new_image

def map_pixels_to_ascii_chars(image, range_width=25):
	# split the gray range by 25
	# convert to correspond char
	pixels_in_image = list(image.getdata())
	pixels_to_chars = [ASCII_CHARS[pixel_value/range_width] for pixel_value in pixels_in_image]
	return "".join(pixels_to_chars)

def convert_image_to_ascii(image, new_width=150):
	image = scale_image(image, new_width)
	image = image.convert('L')

	# out put the new graph
	pixels_to_chars = map_pixels_to_ascii_chars(image)
	len_pixels_to_chars = len(pixels_to_chars)
	image_ascii = [pixels_to_chars[index: index + new_width] for index in xrange(0, len_pixels_to_chars, new_width)]

	return "\n".join(image_ascii)

def commandline(src_path, new_width=150):
	image = None
	try:
		image = Image.open(src_path)
	except Exception, e:
		print e
		return

	image_ascii = convert_image_to_ascii(image, new_width)
	with open(src_path[:-4] + ".txt", "w") as file:
		file.write(image_ascii)

if __name__=='__main__':	
	src_path = sys.argv[1]
	try:
		new_width = int(sys.argv[2])
		commandline(src_path, new_width)
	except:
		commandline(src_path)

		