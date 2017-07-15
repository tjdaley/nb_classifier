# Analyzes a Training File for Balance
#
# Load a training file and show a bar chart of the disribution of
# samples we have for each classification. The purpose is to visually
# show whether a training set is sufficiently well-balanced.
#
# Copyright (c) 2017 by Thomas J. Daley, J.D.
# Author: Thomas J. Daley, J.D. <tjd@jdbot.us>
# URL: <http://www.jdbot.us>
# For license information, see LICENSE.TXT
#

import argparse
import json
import matplotlib.pyplot as plt
import numpy as np
import time

# # # # # # # # # #
# F U N C T I O N S 
# # # # # # # # # #
def analyze_and_plot(filename):
	# Load the training file and keep a count of how many observations we have per class label
	counts = {}
	phrases = {}
	N = 0

	with open(filename, "r") as fin:
		for line in fin:
			N += 1
			try:
				jsonObject = json.loads(line[:-1])
				classLabel = jsonObject["class"]
				if classLabel not in counts:
					counts[classLabel] = 0
				counts[classLabel] += 1
			except:
				print ("Error processing line #{}: {}".format(N, line[:-1]))
				
			k = phraseMunger(line[:-1])
			if k not in phrases:
				phrases[k] = N
				if args.nodupe:
					print (json.dumps(jsonObject))
			else:
				if not args.nodupe:
					print ("Line #{} appears to be a duplicate of line #{}".format(N, phrases[k]))

	# Show the bar chart
	if len(counts) > 0:
		print ("Analyzed", len(phrases), "unique utterances out of", N, "records")
		plt.bar(range(len(counts)), counts.values(), align='center')
		plt.xticks(range(len(counts)), list(counts.keys()))

		plt.show()
		
def phraseMunger(phrase):
	"""
	Function that takes a phrase and returns a string of alphabeticaly sorted lowercase letters.
	"""
	s = phrase.lower().replace(" ", "")
	return ''.join(sorted(s))

# # # # # # # # # #
# M A I N
# # # # # # # # # #

# Set-up argument parser
parser = argparse.ArgumentParser(description="Analyze a training set")
parser.add_argument("file", help="File to process")
parser.add_argument("--nodupe", help="Remove duplicates. Errors will not be printed.", action="store_true")
args = parser.parse_args()

# Input training files
filename = args.file

analyze_and_plot(filename)