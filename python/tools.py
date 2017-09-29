import csv
import sys
import warnings
import random
import string


def readconf(filepath, key):    
	with open(filepath, 'r') as file:
		for line in file:
			tokens = line.split()
			if len(tokens) == 2 and tokens[0] == key:
				return tokens[1].replace('\"', '').replace('/','\\')
				
	warnings.warn('key <' + key + '> not found in ' + filepath)

	return None


def randstr(len = 20):
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(20))