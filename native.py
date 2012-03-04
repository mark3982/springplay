'''
	Here I have to bond the external code written in a form that gives
	higher peformance with Python.

	DXT1_decode(void *in, uint length, void *out)

'''
from ctypes import *

native = {}
hdll = cdll.LoadLibrary('.\\native\\main.dll')
native['DXT1_decode'] = CFUNCTYPE(c_int)(('DXT1_decode', hdll))
native['DXT1_decode'].arglist = [c_void_p, c_uint, c_void_p]