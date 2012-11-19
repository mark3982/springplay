'''
	I wrote this module to handle all persistant storage of data needed by
	the application. Anything needing to be stored should use this module
	to do so.

	I think a namespace division of data would be great such that:

	<plugin-name>.<data-item>
	<plugin-name>.<extra-namespace>.<data-item>
	<plugin-name>...
	
	Or, not nessarily the plugin name but anything.
'''
import os
import time
import random

stordir = None
index = None

def __init__():
	global stordir, index
	stordir = './storage'
	if not os.path.exists(stordir):
		os.mkdir(stordir)
	if os.path.exists('%s/index' % stordir):
		fd = open('%s/index' % stordir, 'r')
		index = eval(fd.read())
		fd.close()
	else:
		index = {}

__init__()

def commit():
	fd = open('%s/index' % (stordir), 'w')
	fd.write('%s' % index)
	fd.close()

LOC_DISK = 100
LOC_MEM = 200
'''
	You can write data into memory (default), or into a disk storage file.
	Use the disk storage for large data since by default everything will
	be memory resident. I hope in the future to have the ability to include
	code to automatically manage swapping some disk data into memory based
	on usage statistics and thresholds. 

	So for bulk data use disk, and light configuration use memory.
'''
def write(key, data, useDisk = False):
	if useDisk:
		nodes = os.listdir(stordir)
		r = random.Random(time.time())
		id = '3982'
		while id in nodes:
			id = str(r.randint(0, 0xffffffff))
		print('write', key, id)
		index[key] = (LOC_DISK, id)
		fd = open('%s/%s' % (stordir, id), 'wb')
		fd.write(data)
		fd.close()
		commit()
		return True
	index[key] = (LOC_MEM, data)
	commit()
	return True

def exist(key):
	if key in index:
		return True
	return False

def read(key):
	if key in index:
		if index[key][0] == LOC_MEM:
			return index[key][1]
		if index[key][0] == LOC_DISK:
			fd = open('%s/%s' % (stordir, index[key][1]), 'rb')
			data = fd.read()
			fd.close()
			return data
		return None
	return None







