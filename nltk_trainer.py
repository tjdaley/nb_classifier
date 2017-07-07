# JDBOT - Intent Classifier Training
#
# Train a Naive Bayes classifier based on an input file
# and save the classifier to an output file (default is bayes.pickle)
#
# Copyright (c) 2017 by Thomas J. Daley, J.D.
# Author: Thomas J. Daley, J.D. <tjd@jdbot.us>
# URL: <http://www.jdbot.us>
# For license information, see LICENSE.TXT
#

import argparse
import equivalencer
import labels
import nb_utilities as util
import nltk
import pickle
import random

# # # # # # # # # #
# M A I N
# # # # # # # # # #

# Defaults
pickleFile = "naivebayes"

# Set-up argument parser
parser = argparse.ArgumentParser(description="Train and pickle a Naive Bayes classifier")
parser.add_argument("file", help="File to process")
parser.add_argument("-o", "--output", help="Output file to persist classifier to. "+pickleFile+"]", default=pickleFile)
parser.add_argument("-s", "--separate", help="Should input files be separated into training and testing sets? [NO]" , action="store_true")
args = parser.parse_args()

# Name of file to save classifier to once it is trained.
pickleFile = args.output

# Input training files
filename = args.file

# Build vocabulary of all words in all documents from all files
vocabulary = util.load_words(filename)
print ("Loaded a vocabular of", len(vocabulary), "words.")
all_words = nltk.FreqDist(vocabulary)
print ("Here are the 50 most common words")
print (all_words.most_common(50))


# Create and shuffle feature sets
word_features = list(all_words.keys())[:3000]
featuresets = util.load_feature_sets(filename, word_features)

#random.shuffle(featuresets)

# Create training and testing sets
training_set = ()
testing_set  = ()

if args.separate:
	num_sets = len(featuresets)
	training_set = featuresets[:int(num_sets/2)]
	testing_set = featuresets[num_sets - len(training_set):]
else:
	training_set = featuresets
	testing_set = featuresets

# Train the classifier
classifier = nltk.NaiveBayesClassifier.train(training_set)

# Test the classifier. If we did not separate the inputs into training and testing
# sets, then we test based on the training data. That will lead to a potentially
# misleadingly high accuracy.
print("Classifier accuracy percent:", (nltk.classify.accuracy(classifier, testing_set))*100)
if (not args.separate):
	print ("\t@@@@@ That accuracy percent is based on testing with the training set.\n\t@@@@@ That will make it misleadingly high.")
	print ("\t@@@@@ Rerun this program with the -s option to get a more accurate read on the classifier's accuracy.")

i = 0
for featureset in featuresets:
	pdist = classifier.classify(featureset[0])
	if pdist != featureset[1]:
		print ("#{}: {} should have been {}".format(i, pdist, featureset[1]))
		for wt in featureset[0].keys():
			if featureset[0][wt]: print (wt, " ", end="");
		print ("\n")
		print ("-----------------------------------")
	i += 1
	
classifier.show_most_informative_features(50)

# Save the trained classifier for later use
fout = open(pickleFile+".pickle", "wb")
pickle.dump(classifier, fout)
fout.close()
fout = open(pickleFile+"_word_features.pickle", "wb")
pickle.dump(word_features, fout)
fout.close()

# Let the user know we're done.
print ("Classifier saved to", pickleFile)