# import the necessary packages
from engine import Engine
import argparse

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--dataset", required=False,
	help = "Path to dataset")
ap.add_argument("-q", "--query", required=True,
	help = "Path to the query image")
ap.add_argument("-n", "--num_results", type=int, required=False,
	help = "num of results")
args = vars(ap.parse_args())

if args["dataset"]:
	engine = Engine(args["dataset"])
else:
	engine = Engine()

if args["num_results"]:	
	engine.search(args["query"], args["num_results"])
else:
	engine.search(args["query"])












