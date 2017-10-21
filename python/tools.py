import os
import errno
import csv
import sys
import warnings
import random
import string
import platform
import datetime
import shutil
import psutil


INVALID = -1


def islinux():
	return platform.system().startswith('Linux')
	

def readconf(filepath, key):    
	with open(filepath, 'r') as file:
		for line in file:
			tokens = line.split()
			if len(tokens) == 2 and tokens[0] == key:
				if islinux():
					return tokens[1].replace('\"', '').replace('\\','/')
				else:
					return tokens[1].replace('\"', '').replace('/','\\')
				
	warnings.warn('key <' + key + '> not found in ' + filepath)

	return None


def randstr(len = 20):
	return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(20))


def friendlytime(time):
    return str(datetime.timedelta(seconds=int(time)))


def remfile(path):

    try:
        os.remove(path)
    except OSError as e:
        if e.errno != errno.ENOENT:
            raise


def copyfile(src, dst):
    try:
        shutil.copy(src, dst)    
    except shutil.Error as e:
        print('Error: %s' % e)    
    except IOError as e:
        print('Error: %s' % e.strerror)


def getroot(confPath):	

    confpath = os.path.expanduser(confPath)
    root = readconf(confpath, 'music_directory')
    
    return root


def procname(pid):
    
    if pid != INVALID:

        try:
            p = psutil.Process(pid)
            return p.name()
        except Exception as e:
            print(e)

    return None


def procid(name):

    pids = psutil.pids()

    for pid in pids:
        try:
            p = psutil.Process(pid)
            if p.name() == name:
                return pid
        except Exception as e:
            print(e)

    return INVALID


def procstart(path, args=[]):

    path = os.path.realpath(path)
    dir = os.path.dirname(path)
    name = os.path.basename(path)

    print('start process ' + name)

    pid = procid(name)

    if pid == INVALID:
        try:
            p = psutil.Popen([path] + args, cwd=dir)
            pid = p.pid
        except Exception as e:
            print(e)
            return INVALID
    
    return pid
    

def procstop(pid):

    name = procname(pid)   

    if name:

        print('stop process ' + name)
    
        try:
            psutil.Process(pid).terminate()
        except Exception as e:
            print(e)    
