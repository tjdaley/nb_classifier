# equivalencer.py
#
# @author: Thomas J. Daley, J.D.
# @date: June 23, 2017
#
# Translates words into their synonyms.
#
# Example:
#	import equivalencer
#	e = equivalencer.Equivalencer()
#	print(e.equivalence("husband"))
#	>>> 'spouse'
#
# @version 1.0.0
class Equivalencer():

	def __init__(self, filename="equivalences.txt"):
		"""
		Class constructor.
		
		Initializes the dictionary of items that is used to find equivalent words.
		The dictionary is populated from a text file ("equivalences.txt") that is formatted
		as such:
		
			equivalence:csv_of_synonyms
			
		for example:
		
			spouse:husband,wife,husbands,wifes,wives
			
		The constructor creates dictonary entries from each line of the file. For example
		the above line would look like this in the dictionary:
		
			{"husband":"spouse", "wife":"spouse", "husbands":"spouse", "wifes":"spouse", "wives":"spouse"}
		"""
		d = {}
		
		with open(filename, "r") as fin:
			for line in fin:
				parts = line[:-1].split(":", 2)
				toText = parts[0]
				for w in parts[1].split(","):
					d[w] = toText
		fin.close()
		self._dictionary = d
		
	def equivalence(self, word, recursion_limit=10):
		"""
		Return the equivalent word that we are using in our natuarl language learning.
		
		Recursively search for equivalences until none are found OR until we have looked
		10 times. I put a limit on the recursion because it's possible that a badly formed
		input text file could create infinite recursion, e.g.:
		
			spouse:husband
			husband:spouse
			
		That kind of circular reference will go on forever and thus the recursion_limit.
		"""
		count = 0
		e = self._get_equivalence(word)
		while e != self._get_equivalence(e) and count < recursion_limit:
			count += 1
			e = self._get_equivalence(e)
			
		return e
		
	def _get_equivalence(self, word):
		if word in self._dictionary:
			return self._dictionary[word]
		else:
			return word