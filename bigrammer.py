# bigrammer.py
#
# @author: Thomas J. Daley, J.D.
# @date: June 23, 2017
#
# Translates two-word sequences (bi-grams) into a single word.
#
# Example:
#	import bigrammer
#	b = equivalencer.Bigrammer()
#	s = "I need to lower my child support"
#	print(b.bigram(s))
#	>>> 'I need to lower my childsupport'
#
# @version 1.0.0
class Bigrammer():

	def __init__(self, filename="bigrams.txt"):
		"""
		Class constructor.
		
		Initializes the list of regular expressions that is used to replace bigrams with single words.
		The dictionary is populated from a text file ("bigrams.txt") that is formatted
		as such:
		
			bi-gram:single_word
			
		for example:
		
			child support:childsupport
			
		The constructor creates list entries from each line of the file. For example
		the above line would look like this in the list:
		
			[["child support", "childsupport"]]
		"""
		l = []
		
		with open(filename, "r") as fin:
			for line in fin:
				parts = line[:-1].split(":", 2)
				fromText = parts[0]
				toText = parts[1]
				l.append([fromText, toText])
		fin.close()
		self._list = l
		
	def bigram(self, document):
		"""
		Replace sequences with corresponding sequences.
		"""
		
		newdoc = "" + document

		for bigram in self._list:
			newdoc = newdoc.replace(bigram[0], bigram[1])
		
		return newdoc