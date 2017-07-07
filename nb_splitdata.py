# nb_splitdata.py
#
# @author: Thomas J. Daley, J.D.
# @date: June 14, 2017
#
# This program separates a Google Calendar file into two data sets: Training and Testing.
#
# @version 1.0.0

import argparse
import datetime
import json
import nb_utilities as util
import numpy as np
#import re
#import string

import stop_words
import labels

# # # # # # # # # #
# G L O B A L S
# # # # # # # # # #
SATURDAY          = 5
TRAINING_FILE     = "training.json"
TESTING_FILE      = "testing.json"
VOCABULARY_MODULE = "vocabulary.py"
PROBABILITY_MODULE= "probabilities.py"

# # # # # # # # # #
# F U N C T I O N S
# # # # # # # # # #
def countTrainingDocs():
	trainingCount = 0
	
	with open(TRAINING_FILE, "r") as fin:
		for line in fin:
			event = json.JSONDecoder().decode(line[:-1])
			labelDocumentCount[event["CLASS"]] += 1
			trainingCount += 1
			
	fin.close()
	print ("Loaded counts from training file.")
	return trainingCount
	
def dumpList(theList, theFile):
	theFile.write("[")
	firstItem = True
	
	for item in theList:
		if (not firstItem):
			theFile.write(",")
		else:
			firstItem = False
			
		if isinstance(item, (list, tuple)) or (item.__class__.__name__ == "ndarray"):
			dumpList(item, theFile)
		else:
			#print (item.__class__.__name__)
			theFile.write("\t%s\n" % item)
			
	theFile.write("]")

def getClass(text):
	print (text)
	for idx in range(0, len(labels.LABELS)):
		print (idx, " - ", labels.LABELS[idx])
	
	label = input("Label? [0] ")
	
	if not label:
		label = 0
	else:
		label = int(label)
	print ("-------------------------------------------------------")
	return label
	
def saveProbabilityModule(pLabels, pNumerator, pDenominator, pVector):
	fout = open(PROBABILITY_MODULE, "w")
	fout.write("# # # # # # # # # #\n")
	fout.write("# Probability Module\n")
	fout.write("#\n")
	fout.write("# Use: import probability\n")
	fout.write("# # # # # # # # # #\n\n")
	fout.write("pLabels = ")
	json.dump(pLabels, fout)
	fout.write("\n\n")
	fout.write("pNumerator = \\\n")
	dumpList(pNumerator, fout)
	fout.write("\n\n")
	fout.write("pDenominator = \\\n")
	dumpList(pDenominator, fout)
	fout.write("\n\n")
	fout.write("pVector = \\\n")
	dumpList(pVector, fout)
	fout.write("\n")
	fout.close()
	return
	
def saveVocabularyModule(vocabList):
	vocabFile = open(VOCABULARY_MODULE, "w")
	vocabFile.write("# # # # # # # # # #\n")
	vocabFile.write("# Vocabulary Module\n")
	vocabFile.write("#\n")
	vocabFile.write("# Use: import vocabulary\n")
	vocabFile.write("# # # # # # # # # #\n\n")
	vocabFile.write("VOCABULARY = \\\n")
	json.dump(vocabList, vocabFile)
	vocabFile.write("\n")
	vocabFile.close()
	return


# # # # # # # # # #
# M A I N
# # # # # # # # # #

# Process command line arguments
parser = argparse.ArgumentParser("Separate training and testing data.")
parser.add_argument("files", help="List of files to process", nargs="*")
parser.add_argument("-l", "--limit", help="Number of lines to process. Default is to process all lints.", \
type=int, default=0)
parser.add_argument("-e", "--events", help="Number of events to process. Default is to process all events up to line limit.", \
type=int, default=0)
parser.add_argument("-s", "--start", help="Name of step to start at", default="*")
parser.add_argument("-k", "--keep", help="Keep stop words (do not filter out stop words)", action="store_true")
parser.add_argument("-t", "--train", help="Treat all entries as training entries", action="store_true")
parser.add_argument("--nolog", help="Do not use log functions to train the engine", action="store_true")
args = parser.parse_args()

# Variables used by all steps
labelDocumentCount = [0] * len(labels.LABELS)
trainingCount = 0

# Should we keep stop words?
KEEPSTOPWORDS = args.keep
print ("@@@@@@@@@@@@@@@@@ Keeping stop words?", KEEPSTOPWORDS)

# Are we just creating training entries?
TRAININGONLY = args.train

# Should we not use the log functions?
NOLOG = args.nolog

# Starting step
STARTINGSTEP = args.start

if (STARTINGSTEP == "*"):
	# List of files to process
	FILELIST = args.files
	if len(FILELIST) == 0:
		print ("You must specify one or more input files on the command line.")
		exit()
		
	# Line limit
	LINELIMIT = args.limit
	if LINELIMIT != 0:
		print ("Will process up to", LINELIMIT, "lines in each file")
	else:
		print ("Processing all lines in all files")
		
	# Event Limit
	EVENTLIMIT = args.events
	if EVENTLIMIT != 0:
		print ("Will process up to", EVENTLIMIT, "events in each file (up to line limit)")
	else:
		print ("Processing all events in all files (up to line limit)")
		
	# Get labels
	#LABELS = getLabels()
		
	# Open output files
	trainingFile = open(TRAINING_FILE, "w")
	testingFile  = open(TESTING_FILE, "w")
		
	# Process each input file
	lineCount = 0
	testCount = 0
	eventCount = 0
	event = {}
	skipped = False

	for filename in FILELIST:
		with open(filename, "r") as fin:
			for line in fin:
				lineCount += 1

				# See if we have processed enough lines already. If so, exit.
				if (lineCount > LINELIMIT and LINELIMIT != 0):
					print("Line limit (", LINELIMIT, ") reached")
					break
				
				# Clean up the input data a little.	
				line = line[:-1]				# Remove terminating newline
				line = line.replace("\\n", " ")	# Strips Google's new-line indicator
				line = line.replace("\\", "")	# Strips all other escape characters
				
				# If this line is just a continuation of the previous data line
				# append it to the data for the current label.
				if (line[:1] == " ") and skipped == False:
					event[label] += line[1:]
				# If this marks the beginning of a new event, clear out the event object
				elif (line == "BEGIN:VEVENT"):
					eventCount += 1
					event = {}
				# If this marks the end of a new event, save odd-numbered events to the
				# training file and even-numbered events to the testing file.
				elif (line == "END:VEVENT"):
					if ("TEXT" in event):
						savedText = event["TEXT"]
						event["TEXT"] = util.extract_words(event["TEXT"])
						
						if (eventCount % 2 == 0 and not TRAININGONLY):
							json.dump(event, testingFile)
							testingFile.write("\n")
							testCount += 1
						else:
							if "CLASS" not in event:
								event["CLASS"] = getClass(savedText)
							labelDocumentCount[event["CLASS"]] += 1
							json.dump(event, trainingFile)
							trainingFile.write("\n")
							trainingCount += 1
							
					if (eventCount > EVENTLIMIT and EVENTLIMIT !=0):
						print ("Event limit (", EVENTLIMIT,") reached")
						break
						
				# Otherwise, split the data from its label. Not all labels have data.
				else:
					parts = line.split(":", maxsplit=1)
					label = parts[0]
					data = None
					skipped = True
					if (len(parts) == 2):
						data = parts[1]
					
					# If we care about the data associated with this label, save it to our event.
					if (label == "DESCRIPTION" or label == "SUMMARY" or label == "LOCATION") and data != None:
						label = "TEXT"
						if (label in event):
							event[label] += " " + data 
						else:
							event[label] = data
						skipped = False
					# Change the start date to a WORKDAY flag.
					elif (label[:7] == "DTSTART") and data != None:
						skipped = False
						eventDate = datetime.datetime.strptime(data[:8], '%Y%m%d').date()
						if (eventDate.weekday() < SATURDAY):
							event["WORKDAY"] = 1
						else:
							event["WORKDAY"] = 0
					# Save pre-determined class
					elif (label == "CLASS"):
						event["CLASS"] = int(data)
		
		#end of file
		fin.close()
		
	#end of processing loop
	trainingFile.close()
	testingFile.close()

	print ("Processed", lineCount, "lines into", eventCount, "events.")
	print ("Created", testCount, "test events and", trainingCount, "training events.")

# # # # # # # # # #
# Create a vocabulary module from the training data.
# # # # # # # # # #

if (STARTINGSTEP == "avocab"):
	trainingCount = countTrainingDocs()
	
if (STARTINGSTEP == "*" or STARTINGSTEP == "avocab"):
	STARTINGSTEP = "*"
	print ("Building vocabulary.")

	vocabSet = set({})

	# Create list of all words in the vocabulary.
	with open(TRAINING_FILE, "r") as fin:
		for line in fin:
			event = json.JSONDecoder().decode(line[:-1])
			vocabSet = vocabSet | set(event["TEXT"])

	fin.close()
	
	vocabList = sorted(vocabSet) #list(vocabSet)

	# Save the vocabulary so that it can be restored without reanalyzing all the inputs.
	saveVocabularyModule(vocabList)

	print ("Created a vocabulary of ", len(vocabList), "words, which is saved in", VOCABULARY_MODULE)

# # # # # # # # # #	
# Create a vector of flags for each document in the training set.
# The length of the vector is the length of the vocabular list.
# Then count how many times each word from the vocabulary appears in each document.
# # # # # # # # # #
if (STARTINGSTEP == "*" or STARTINGSTEP == "cprob"):
	STARTINGSTEP = "*"
	print ("Comparing each document to the vocabulary to count word frequency.")

	trainingFile = open("v_"+TRAINING_FILE, "w")

	with open(TRAINING_FILE, "r") as fin:
		for line in fin:
			event = json.JSONDecoder().decode(line[:-1])
			event["VOCABVECTOR"] = util.create_vocabulary_vector(event["TEXT"], vocabList)
			json.dump(event, trainingFile)
			trainingFile.write("\n")
			
	fin.close()
	trainingFile.close()

	print ("\tWord vectors saved in v_"+TRAINING_FILE)

# # # # # # # # # #
# Train the engine
# # # # # # # # # #
if (STARTINGSTEP == "*" or STARTINGSTEP == "train"):
	STARTINGSTEP = "*"
	print ("Training the NB Classifier.")

	numWords  = len(vocabList)
	numLabels = len(labels.LABELS)

	pLabel       = [0.0] * numLabels
	pNumerator   = [0.0] * numLabels
	pDenominator = [0.0] * numLabels

	# Initialize probabilities
	for labelIndex in range(numLabels):
		pLabel[labelIndex] = labelDocumentCount[labelIndex] / float(trainingCount)
		pNumerator[labelIndex] = np.ones(numWords)
		pDenominator[labelIndex] = 2.0
		
	# For each label, count the number of vacabulary occurances in all documents
	vTrainingFile = "v_" + TRAINING_FILE

	with open(vTrainingFile, "r") as fin:
		recno = 0
		for line in fin:
			recno += 1
		
			try:
				event = json.JSONDecoder().decode(line[:-1])
				pNumerator[event["CLASS"]] += event["VOCABVECTOR"]
				pDenominator[event["CLASS"]] += sum(event["VOCABVECTOR"])
			except:
				print ("----------------", recno, "----------------")
				print (line)
				print ("--------------------------------")
	
	fin.close()
				
	pVector = [0.0] * numLabels
	for labelIndex in range(numLabels):
		if (pDenominator[labelIndex] != 0):
			if NOLOG:
				pVector[labelIndex] = (pNumerator[labelIndex] / pDenominator[labelIndex])
			else:
				pVector[labelIndex] = np.log(pNumerator[labelIndex] / pDenominator[labelIndex])
		else:
			pVector[labelIndex] = np.zeros(numWords)

	saveProbabilityModule(pLabel, pNumerator, pDenominator, pVector)

print ("Training is complete")