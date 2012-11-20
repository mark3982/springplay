import os
import sys
import subprocess
import struct
import native
from ctypes import *
from PyQt4 import QtGui
import storage
import zipfile

'''
	Handles enumerating all the maps on the system. Need to change it
	so the map directory must be provided (so the class is platform
	independant), and then rely on configuration panel for input of
	the correct map directory or directories.
'''
gMapMan = None

def getMapManager():
	global gMapMan
	
	if gMapMan is None:
		gMapMan = mapManager(False)
	return gMapMan

class mapManager:
	def __init__(self, useHTTPForMaps):
		self.refresh()
		self.useHTTPForMaps = useHTTPForMaps

	'''
		* need more configuration here.. still need to flush this out
	'''
	def refresh(self):
		if sys.platform == 'win32':
			self.mapdir = '%s\\My Documents\\My Games\\Spring\\maps\\' % (os.environ['USERPROFILE'])
		else:
			print('opps... platform not supported for map manager..')
			exit()
		self.maps = os.listdir(self.mapdir)
	'''
		create temp directory
		copy archive into it
		extract archive using external tool
		scan files created from extraction
		do nessary work to files
		delete files and directory
	'''
	def structRead(self, fmt, data, ndx):
		sz = struct.calcsize(fmt)
		out = struct.unpack_from(fmt, data, ndx)
		out = list(out)
		out.append(ndx + sz)
		return out

	'''
		The original layout was done well, but not perfect found here:
			http://springrts.com/wiki/Map_File_Format

		Essentially, it can be rather confusing in the sense that sometimes it is not
		immediantly clear what the author meant, but he did a GREAT job. But, to make
		it easier I have redone it.

		Each type, excluding float, can be prefixed with a 'u'. This means unsigned, but it
		really will not cause you to read the data wrong per say if you happen to treat 
		something as signed. It can cause you to interpret the data wrong once read! So,

		uint32 is unsigned
		int32 is signed

		The int part means integer, and the number afterward is the number of bits and also
		number of bytes indirectly. The 32 means 32 bits and also means 4 bytes. So uint32
		means 4 bytes representing an integer. Then the prefix says if it is unsigned or
		signed meaning the most significant bit is used as a sign.

		[u]int<bits>


		For floating point numbers the designation is float with the number of bits afterward,
		so float32 is a 32 bit float or 4 byte float and float64 is a 8 byte float or DOUBLE in
		the C language.

		Also this structure has NO padding! Depending on your language you are using or mechanisms,
		or modules (python) you may need to pay careful attention that it does not assume padding
		has been added! Or, the entire structure will be read into memory incorrectly. But, I do
		not think you will have that problem. Just check it in case.
		
		_SMFHDR {
			uint8		magic[16];
			uint32		version = 1;
			uint32		mapID;
			uint32		xSize;
			uint32		ySize;
			uint32		squareSize = 8;
			uint32		texel = 8;
			uint32		tileSize;
			float32		minHeight;
			float32		maxHeight;
			uint32		extraHdrs = 1;
			uint32		heightPtr;
			uint32		typePtr;
			uint32		miniPtr;
			uint32		tilesPtr;
			uint32		metalPtr;
			uint32		featuresPtr;		
		}
		
		This header comes right after the header above. There is a count of 
		these equal to 'extraHdrs' above. Which is supposed to be one/1. But,
		also good place to double check at least for corrupted or bad data.
		EXTRAHDR {
			uint32		extraHdrSize = 12;
			uint32		extraHdrType = MEH_Vegetation;
			uint32		extraHdrPtr;			
		}

		MEH_Vegetation is just something the original author has in diagram, and
		I think it was good to leave it. I am not sure of the meaning exactly, but
		for some reason that may be the value the field is expected to have.

		Had a SMF file give a wild extra header count of 703252. The solution was
		to ignore it. Although I did not throughly test this solution.
	'''
	def brkcolor(self, color):
		# RRRRRGGGGGGBBBBB
		r = color >> (5 + 6)
		g = (color >> 5) & 0x03f
		b = color & 0x01f
		return r, g, b
	'''
		For some reason my QImage will not accept setPixel using RGB16 format, but instead
		wants to use RGBA32. So.. got to convert here from RGB16 to RGBA32 which also involes
		scaling the values up from 5-bit and 6-bit to 8-bit, or else the image will be dark
		looking.

		
	'''
	def pakcolor(self, c):
		cr = int(c[0]) << 3			# 5-bit to 8-bit
		cg = int(c[1]) << 2			# 6-bit to 8-bit
		cb = int(c[2]) << 3			# 5-bit to 8-bit
		return int(cb) | (int(cg) << 8) | (int(cr) << 16)
	'''

	'''
	def getcolorlen(self, c):
		return math.sqrt(c[0]*c[0]+c[1]*c[1]+c[2]*c[2])
	def getcolors(self, c1, c2):
		c1 = self.brkcolor(c1)
		c2 = self.brkcolor(c2)
		rt = c2[0] - c1[0] 
		gt = c2[1] - c1[1]
		bt = c2[2] - c1[2]
		c4 = c2
		# .33 and other .66
		c2 = [rt * .33 + c1[0], gt * .33 + c1[1], bt * .33 + c1[2]]	
		c3 = [rt * .66 + c1[0], gt * .66 + c1[1], bt * .66 + c1[2]]
		c1 = self.pakcolor(c1)
		c2 = self.pakcolor(c2)
		c3 = self.pakcolor(c3)
		c4 = self.pakcolor(c4)
		return c1, c2, c3, c4
	def decodeDXT1(self, data, w, h):
		'''
			4x4 pixel block (512 bits / 16 pixels / 32 bit color)
				* creates two 16-bit colors (two others are interpolate between these two)
			[32 bits of index colors]
				[16 bit color using 565 color format]
				[16 bit color using 565 color format]
			[32 bits of pixel data]
				[2 bit index into color table]
			
			64:512 = 1:8 (compression ratio)

			ndx:
				0 = color1
				1 = color2
				2 = color1 * .66 + color2 * .33
				3 = color1 * .33 + color1 * .66
		'''
		# QImage.Format_ARGB32, QImage.Format_RGB32	

		# You want it fast in native code? Or, slow, but always portable? If it
		# has been loaded into memory and stored then we will use it.
		if 'DXT1_decode' in native.native:
			out = create_string_buffer(w * h * 2)
			native.native['DXT1_decode'](c_char_p(data), c_uint(len(data)), c_uint(w), c_uint(h), out)
			qimg = QtGui.QImage(out, 1024, 1024, QtGui.QImage.Format_RGB16)
			print('native done')
			return qimg, out
			

		qimg = QtGui.QImage(1024, 1024, QtGui.QImage.Format_RGB16)
		out = []
		i = 0
		while i < int(len(data) / 8):
			color1, color2, pdata = struct.unpack_from('<HHI', data, i * 8)

			c1, c2, c3, c4 = self.getcolors(color1, color2)
			
			# 565: red:green:blue
			# color1 = (color1 >> (32 - 5), color1 >> (32 - 5 - 6) & 0x03f, color1 & 0x01f)
			# color2 = (color2 >> (32 - 5), color2 >> (32 - 5 - 6) & 0x03f, color2 & 0x01f)

			# 256x256 (blocks) produce 1024x1024 (pixels)
	
			y = int(i / 256)			# block y
			x = i - (y * 256)			# block x
			y = y * 4				# block first pixel
			x = x * 4				# block first pixel

			i = i + 1
			z = 0
			while z < 16:
				ndx = pdata & 0x03
				if ndx == 0:
					ndx = c1
				elif ndx == 1:
					ndx = c2
				elif ndx == 2:
					ndx = c3
				elif ndx == 3:
					ndx = c4
				pdata = pdata >> 2

				
				col = (z & 0x03) + x
				row = ((z & 0x0c) >> 2) + y
				# 
				qimg.setPixel(col, row, ndx)
				z = z + 1
		return qimg

	'''
		* reads SMF format and returns parameters and data

		Need to clean this up. Its just quick and dirty right now. Needs to
		return more information about the SMF if possible, or something. Maybe
		even delay processing until a specific member is accessed, because 
		DXT1 decoding is already slow in pure python!

		Also, may want to support extending cache to disk. So if it stays in pure
		python at least it will not be done all the time. Also consider making a
		seperate thread if python allows it to improve performance, and if accessed
		before seperate thread is done then provide a black image or default data.
	'''
	qimg_cache = {}
	def readSMF(self, path):
		fd = open(path, 'rb')
		data = fd.read()
		fd.close()

		ndx = 0
		sig, ndx = self.structRead('<16s', data, ndx)
		var, ndx = self.structRead('<I', data, ndx)
		mapid, ndx = self.structRead('<I', data, ndx)
		xsize, ysize, ndx = self.structRead('<II', data, ndx)
		squareSz, texelSq, tileSz, minHeight, maxHeight, extraHdrCnt, ndx = self.structRead(
			'<IIIffI', data, ndx
		)
		heightPtr, typePtr, miniPtr, tilesPtr, metalPtr, featurePtr, ndx = self.structRead(
			'<IIIIII', data, ndx
		)
		print(squareSz, texelSq, tileSz, minHeight, maxHeight, extraHdrCnt)
		print(heightPtr, typePtr, miniPtr, tilesPtr, metalPtr, featurePtr)
		
		'''
		extraHdrs = []
		x = 0
		while x < extraHdrCnt:
			ehSize, ehType, ehVegPtr, ndx = self.structRead(
				'<III', data, ndx
			)
			extraHdrs.append((ehSize, ehType, ehVegPtr))
			x = x + 1		
		'''
		# the fixed compression from the DXT1 format (1:8)
		# 1024x1024x4 becomes 256x256x8 which is 8/1
		miniMapData = data[miniPtr:miniPtr + int((1024*1024*4)/8)]
		qimg, qimgraw = self.decodeDXT1(miniMapData, 1024, 1024)
		return qimg, qimgraw	

	def getMiniMap(self, name):
		storkey = 'mapManager.minimap.%s' % name
		if storage.exist(storkey):
			qimg = QtGui.QImage(storage.read(storkey), 1024, 1024, QtGui.QImage.Format_RGB16)
			return qimg
		# okay look and see if we have the map file locally
		if name not in self.maps:
			print('getMiniMap-name-not-found', name)
			return None
		dstdir = os.path.abspath('.\\7ztmp')
		archive = '%s%s' % (self.mapdir, name)
		if os.path.exists(dstdir):
			self.rmdir(dstdir)
		os.mkdir(dstdir)

		if archive[-4:] == '.sd7':
			subprocess.call(['7zr.exe', '-ir!*.smf', '-y', 'e', '-o%s' % dstdir, archive])
		if archive[-4:] == '.sdz':
			zf = zipfile.ZipFile(archive)
			for node in zf.namelist():
				ext = node[-4:]
				# skipping tile file... maybe little faster.. (if it goes missing look here for sdz files)
				if ext != '.smd' or ext != '.smf':
					continue
				data = zf.read(node)
				node = node.replace('/', '_').replace('\\', '_')
				fd = open('%s\\%s' % (dstdir, node), 'wb')
				fd.write(data)
				fd.close()

		nodes = os.listdir(dstdir)
		'''
			.smd is plain text, lots of interesting information that the user
			could be interested in especially hardcore players, also seems 
			very useful info too about start positions!
			.smf is the actual map file with height data and minimap data
			.smt is the tile file.. i dont know anything about this one yet
			
		'''
		for node in nodes:
			ext = node[-4:]
			if ext == '.smd':
				pass	
			if ext == '.smf':
				qimg, qimgraw = self.readSMF('%s\\%s' % (dstdir, node))
				storage.write('mapManager.minimap.%s' % name, qimgraw, useDisk = True)
				return qimg
			if ext == '.smt':
				pass
		print('game archive did not contain SMF file!')
		self.rmdir('%s' % dstdir)
		return None
	
	def rmdir(self, path):
		nodes = os.listdir(path)
		for node in nodes:
			if os.path.isdir('%s\\%s' % (path, node)):
				self.rmdir('%s\\%s' % (path, node))
			else:
				os.remove('%s\\%s' % (path, node))		
		os.rmdir(path)

	def getMapNames(self):
		return self.maps