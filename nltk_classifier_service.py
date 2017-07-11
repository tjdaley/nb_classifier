# JDBOT - Classifier
#
# Restores a trained NLTK classifier, listens for classification requests,
# processes the requests, and saves the result to a file for later
# supervised fine-tuning.
#
# Copyright (c) 2017 by Thomas J. Daley, J.D.
# Author: Thomas J. Daley, J.D. <tjd@jdbot.us>
# URL: <http://www.jdbot.us>
# For license information, see LICENSE.TXT
#

import argparse
import labels
import nb_utilities as util
import nltk
import pickle

from flask import Flask, request
from flask_restful import Resource, Api
from json import dumps
from flask_jsonpify import jsonify

# # # # # # # # # #
# I N I T I A L I Z E   F L A S K   F R A M E W O R K
# # # # # # # # # #
app = Flask(__name__)
api = Api(app)

# # # # # # # # # #
# G L O B A L S
# # # # # # # # # #
LOGGING = False
LOGFILE = 0

# # # # # # # # # #
# F U N C T I O N S
# # # # # # # # # #
def restore_classifier(filename):
	"""
	Restore a trained classifier from a pickle file.
	
	Given a filename, restore a trained classifier from the file.
	
	:param filename: Name of file that contains the pickeled classifier.
	:type  filename: string
	:return: NLTK Classifier
	:rtype: classifier
	"""
	filename = filename.replace("\.pickle","")
	fin = open(filename+".pickle", "rb")
	classifier = pickle.load(fin)
	fin.close()
	return classifier
	
def restore_word_features(filename):
	"""
	Restore a set of word features created during the training process.
	
	Given a filename, restore a set of word features from the file.
	
	:param filename: Name of file that contains the pickeled word features.
	:type  filename: string
	:return: word_features
	:rtype: list
	"""
	filename = filename.replace("\.pickle","")
	fin = open(filename+"_word_features.pickle", "rb")
	wf = pickle.load(fin)
	fin.close()
	return wf
	
def log_response(document, classification, confidence):
	if LOGGING:
		LOGFILE.write('{"description": "{}", "class": "{}", "score":{}}\n'.format(document, classification, confidence))
		
def open_log_file(filename):
	global LOGFILE
	if LOGGING:
		LOGFILE = open(filename, "w")

def close_log_file():
	if LOGGING:
		LOGFILE.close()
		
# # # # # # # # # #
# I N T E R N A L   C L A S S E S
# # # # # # # # # #
class Classify(Resource):
	def get(self):
		verbose  = request.args.get("verbose") != None
		zeros    = request.args.get("zeros")   != None
		document = request.args.get("q")
		words    = util.extract_words(document)
		likely   = classifier.classify(util.find_features(util.extract_words(document), word_features))
		pdist    = classifier.prob_classify(util.find_features(util.extract_words(document), word_features))
		log_response(document, likely, pdist.prob(likely))
		
		# Create a LUIS-compatible response
		result = {'topScoringIntent': {'intent':likely, 'score':'%.4f'%(pdist.prob(likely))}}
		result["query"] = document
		result["entities"] = []
		if verbose:
			result["intents"] = [{'intent':sample, 'score':'%.4f'%(pdist.prob(sample))} for sample in pdist.samples() if ((pdist.prob(sample) > 0.00009) or zeros)]
			result["words"]   = [word for word in words]

		return jsonify(result)

# # # # # # # # # #
# M A I N
# # # # # # # # # #

# Defaults
pickleFile = "naivebayes"
responseFile = "classifier_responses.json"

# Set-up argument parser
parser = argparse.ArgumentParser(description="Restore and use an NLTK classifier")
parser.add_argument("-p", "--pickle", help="Pickle file to restore classifier from. ["+pickleFile+"]", default=pickleFile)
parser.add_argument("-o", "--output", help="Name of file to log classification responses to for further supervised training")
parser.add_argument("-l", "--listen", help="TCP port to listen on. [8282].", type=int, default=8282)
args = parser.parse_args()

# Restore classifier and word_features
pickleFile = args.pickle
classifier = restore_classifier(pickleFile)
word_features = restore_word_features(pickleFile)

# Open log file
if args.output:
	LOGGING = True
	open_log_file(args.output)
	print ("Logging responses to", args.output)
	
# Add restful service routes
api.add_resource(Classify, '/classify')

# Start the service
if __name__ == '__main__':
	app.run(port=args.listen)