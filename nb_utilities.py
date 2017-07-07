# nb_utilities.py
#
# @author: Thomas J. Daley, J.D.
# @date: June 23, 2017
#
# NB Utilities.
#
# @version 1.0.0

import bigrammer
import equivalencer
import labels
import numpy 		 as np
import nltk
import probabilities as prob
import re
import stop_words
import string

BIGRAMMER    = False
EQUIVALENCER = False

def load_words(filename):
	"""
	Load all words from an ics formatted file.
	
	ics files are formatted like this:
	
		BEGIN:VEVENT
		DESCRIPTION:text we are to process and classify
		CLASS:integer which is an index into labels.LABELS[]
		END:VEVENT
	
	The file will have one or more paragraphs like that.
	
	This function parses the input file and creates a list of every
	word we extract from each document, including duplicates.
	
	:param filename: Name of the file to process.
	:type  filename: string
	:return: list of all extracted words found in all documents
	:rtype: list
	"""
	all_words = []
	prefix = "DESCRIPTION:"
	prefix_length = len(prefix)
	with open(filename, "r") as fin:
		for line in fin:
			if line[:prefix_length] == prefix:
				description = line[prefix_length:-1]
				all_words += extract_words(description)
	fin.close()
	return all_words

def find_features(documentWords, word_features):
	"""
	Get a list of features (words) from a document.
	
	Given a list of words from a document, create a dictionary
	wherein each entry is a word from our vocabulary and the 
	value is a boolean indicating whether that word exists in
	the document provided.
	
	:param documentWords: A list of all words in a document
	:type  documentWords: list
	:return: list of vocabulary words and an indication whether
		this document contained each word
	:rtype: dictionary
	"""
	words = set(documentWords)
	features = {}
	for w in word_features:
		features[w] = (w in words)
		
	return features
	
def load_feature_sets(filename, word_features):
	"""
	Build a list of featuresets from an ics-formatted file.
	
	Given a filename to be loaded, which file is in the ics format
	documented above, create a list of features. The list of features
	is an list. Each item of the list is a set wherein the first entry
	is a list of features from find_features() and the second entry is
	the NAME of the classification, from labels.LABELS[].
	
	:param filename: Name of the file to process.
	:type  filename: string
	:return: list of all features and their corresponding classifications.
	:rtype: list of sets
	"""
	featuresets = []
	
	desc_prefix = "DESCRIPTION:"
	desc_prefix_len = len(desc_prefix)
	class_prefix = "CLASS:"
	class_prefix_len = len(class_prefix)
	
	description = ""
	classification = ""
	
	with open(filename, "r") as fin:
		for line in fin:
			if line[:desc_prefix_len] == desc_prefix:
				description =line[desc_prefix_len:-1]
			elif line[:class_prefix_len] == class_prefix:
				classification = line[class_prefix_len:-1]
				if classification not in labels.LABELS:
					print ("%-Invalid docuoment classification:", classification)
			elif line[:-1] == "END:VEVENT":
				featuresets.append((find_features(extract_words(description), word_features), classification))
	fin.close()
	
	return featuresets


def extract_words(s, KEEPSTOPWORDS = False):
	"""Keep"""
	global EQUIVALENCER
	global BIGRAMMER
	
	if not EQUIVALENCER:
		EQUIVALENCER = equivalencer.Equivalencer()
	
	if not BIGRAMMER:
		BIGRAMMER = bigrammer.Bigrammer()
	
	# Remove colons and pluses
	v = s.replace(":", " ").replace("+"," ").lower()
	
	# Convert dashes to whitespace
	match = re.search("\D+\-\w+", v)
	while (match):
		oldText = "" + match.group()
		newText = oldText.replace("-", " ")
		v = v.replace(oldText, newText)
		match = re.search("\D+\-\w+", v)
		
	# CXL in an appointment means it was cancelled. Some of us put a space after the CXL flag,
	# but others do not. Convert them all so that CXL is followed by whitespace.
	match = re.search("CXL\w", v, re.IGNORECASE)
	if (match):
		oldText = "" + match.group()
		newText = "CXL " + match.group()[3:]
		v = v.replace(oldText, newText)
		
	# Last substitutions before we tokenize the string. The Bigrammer just does a bunch of s.replace()
	# operations, so you can put any replacements that you want in bigrammer.txt.
	v = BIGRAMMER.bigram(v)
		
	# From https://stackoverflow.com/questions/6181763/converting-a-string-to-a-list-of-words
	allWords = [re.sub('^[{0}]+|[{0}]+$'.format(string.punctuation), '', w) for w in v.split()]
	
	# Now eliminate stop words, short words, and numeric words
	# Normalize the words through stemming
	stemmer = nltk.PorterStemmer()
	filteredWords = []

	for word in allWords:
		word = EQUIVALENCER.equivalence(word.lower())
		#print (word, ((word not in stop_words.stop_words) or KEEPSTOPWORDS) and len(word) > 0)
		if ((word not in stop_words.stop_words) or KEEPSTOPWORDS) and (len(word) > 1) and (not isnumeric(word)):
			filteredWords.append(stemmer.stem(word))
			
	return filteredWords

# # # # # # # # # #
# OLD FUNCTIONS FROM ORIGINAL CLASSIFIER
# Can probably be tossed
# # # # # # # # # #


def create_vocabulary_vector(wordVector, vocabList):
	vocabVector = [0]*len(vocabList)

	for word in wordVector:
		if word in vocabList:
			vocabVector[vocabList.index(word)] += 1
	
	return vocabVector

# The Naive Bayes Classifier. Pretty simple once you get it trained!
def classifyNB(vec2Classify):
	pclass = [0.0] * len(labels.LABELS)
	
	for labelIndex in range(len(labels.LABELS)):
		# Really should not have categories with a zero probability. That indicates
		# a categorization error. But it can happen and we don't need it to trigger
		# errors in our program.
		if (prob.pLabels[labelIndex] != 0.0):
			pclass[labelIndex] = sum(vec2Classify * prob.pVector[labelIndex]) + np.log(prob.pLabels[labelIndex])

	return pclass

def isnumeric(s):
    try:
        float(s)
        return True
    except ValueError:
        return False
	
# returns the index of the maximum, non-zero number
def max_index(theArray):
	maxi = 0
	prevVal = theArray[0]
	
	for i in range(len(theArray)):
		if (theArray[i] > prevVal and theArray[i] != 0):
			maxi = i
			prevVal = theArray[i]
		
	return maxi