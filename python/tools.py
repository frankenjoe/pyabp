import os
import errno
import csv
import sys
import traceback
import warnings
import random
import string
import platform
import datetime
import shutil
import psutil
import subprocess
import glob
import logging
import win32api


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
    root = os.path.expanduser(readconf(confpath, 'music_directory'))    
    
    return root


def getfiles(root, extensions=['*']):

    files = []

    if os.path.exists(root):
        for ext in extensions:
            files.extend(glob.glob(os.path.join(root, '*.' + ext)))

    return files


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


def procstart(path, args=[], showConsole=True):

    path = os.path.realpath(path)
    dir = os.path.dirname(path)
    name = os.path.basename(path)

    pid = procid(name)

    if pid == INVALID:
        try:
            startupinfo = subprocess.STARTUPINFO()
            if not showConsole:
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            p = psutil.Popen([path] + args, cwd=dir, startupinfo=startupinfo)
            pid = p.pid
        except Exception as e:
            print(e)
            return INVALID
    
    return pid
    

def procstop(pid):

    name = procname(pid)   

    if name:
    
        try:
            psutil.Process(pid).terminate()
        except Exception as e:
            print(e)    


def drives(removeableonly=False):
        
    partitions = []
        
    for partition in psutil.disk_partitions():     
        tokens = partition.opts.split(',')            
        if islinux():
            if not removeableonly or 'flush' in tokens:
                partitions.append(partition.mountpoint)
        else:
            if not removeableonly or 'removable' in tokens:
                partitions.append(partition.mountpoint)

    return partitions


def drivebyname(name, removeableonly=False):

    ds = drives(removeableonly)

    for d in ds:
        if not islinux():
            n = win32api.GetVolumeInformation(d)[0]
            if name == n:
                return d

    return None


def info(message : str, logger = None):
    if logger:
        logger.info(message)
    else:
        print(message) 


def error(message : str, logger = None):

    if logger:        
        logger.exception(message)
    else:
        traceback.print_exc()
        print('ERROR ' + str(message)) 