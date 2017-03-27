import os

IMG_SUFFIX = ["png", "jpg", "jpeg", "bmp"]

def rename_directory(root_dir):
	paths = [root_dir + '/' + direct for direct in os.listdir(root_dir) if direct.endswith(tuple(IMG_SUFFIX))]
	
	for index, path in enumerate(paths):
		new_path = path[:path.rfind('/')+1] + str(index).rjust(6,'0') + "." + path.split(".")[-1]
		os.rename(path, new_path)

rename_directory("./1")