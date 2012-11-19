'''
	Here I have to bond the external code written in a form that gives
	higher peformance with Python.

	DXT1_decode(void *in, uint length, void *out)
'''
import os
from ctypes import *
import sys

native = {}
'''
	We have to determine the platform and the version!? I am running
	Win7 x64 build and it returns win32. Under WINNT you can not load
	a x86 DLL into a x84 build of Python which is my situation.

	So, we know we are on windows. But, what version is Python may be the
	better question..
'''
platform = 'win32'
if sys.platform == 'win32':
	pass

# Here is where we jump off the boat..
if platform == None:
	print('UHOH... I do not know what platform I am running on...')
	print('I have features which require native librarys. Edit the')
	print('file native.py if need be to set the correct platform!')
	print('OR, SUBMIT A PATCH! =) OR, GET ON MAILING LIST.')
	exit(-1)

hdll = cdll.LoadLibrary('.\\native\\x64win7.dll')
native['DXT1_decode'] = CFUNCTYPE(c_int)(('DXT1_decode', hdll))
native['DXT1_decode'].arglist = [c_void_p, c_uint, c_void_p]