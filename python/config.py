import csv
import sys
import warnings

def read(filepath, key):    
	with open(filepath, 'r') as file:
		for line in file:
			tokens = line.split()
			if len(tokens) == 2 and tokens[0] == key:
				return tokens[1].replace('\"', '')
				
	warnings.warn('key <' + key + '> not found in ' + filepath)

	return None

