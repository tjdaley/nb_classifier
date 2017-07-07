# nb_classifier.py
#
# @author: Thomas J. Daley, J.D.
# @date: June 23, 2017
#
# This program uses the Naive Bayes algorithm to classify text.
#
# @version 1.0.0

import argparse
import json
import nb_utilities	as util
import numpy 		as np

import stop_words
import labels
import vocabulary    as vocab
import probabilities as prob

# # # # # # # # # #
# G L O B A L S
# # # # # # # # # #

# # # # # # # # # #
# F U N C T I O N S
# # # # # # # # # #
def prompt_for_test_phrases():
	myText = input("What do you want to classify? ")
	while myText:
		wordVector = util.extract_words(myText)
		vocabVector = np.array(util.create_vocabulary_vector(wordVector, vocab.VOCABULARY))
		p = util.classifyNB(vocabVector)
		labelIndex = util.max_index(p)
		print ("Most likely:", labels.LABELS[labelIndex])
		for i in range(len(labels.LABELS)):
			print ("\n",labels.LABELS[i],"-->",p[i])
			
		myText = input("\n\nWhat do you want to classify? ")

def process_testing_file():
	with open("testing.json", "r") as fin:
		for line in fin:
			event = json.JSONDecoder().decode(line[:-1])
			vocabVector = np.array(util.create_vocabulary_vector(event["TEXT"], vocab.VOCABULARY))
			p = util.classifyNB(vocabVector)
			labelIndex = util.max_index(p)
			print (event["TEXT"])
			print ("Most likely:", labels.LABELS[labelIndex])
			for i in range(len(labels.LABELS)):
				print ("\n\t\t",labels.LABELS[i],"-->",p[i])
			print ("+++++++++++++++++++++++++++++++++++++++++++++++")
		
# # # # # # # # # #
# M A I N
# # # # # # # # # #

#process_testing_file()
prompt_for_test_phrases()