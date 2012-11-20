import Plugin
import MapManager
import random
import time
import math
import Session
from PyQt4 import QtCore
from PyQt4 import QtGui

class PluginSession(Plugin.Plugin):
	'''
		* can do various chores like maintain sycnhronous network socket
	'''
	rotiter = 0.0
	lobbyLoginGoodOrBad = 0
	lobbyCbs = []
	
	def __init__(self, name, author, description, version, gplugins):
		Plugin.Plugin.__init__(self, name, author, description, version, gplugins)
		self.mm = MapManager.getMapManager()
		self.mm_names = self.mm.getMapNames() 
		random.seed(time.time())
		self.mm_dndx = random.randint(0, len(self.mm_names) - 1)

	def update(self):
		self.qTimer.singleShot(20, self.update)
		# paint something pretty and neat moving
		if self.lobby is None:
			self.lobbyLoginGoodOrBad = 0
			return
		self.wParent.repaint()
		self.rotiter = self.rotiter + 0.01
		session.Update(self.lobby, self.lobbyCb)

	def registerCb(self, obj, _cb):
		self.lobbyCbs.append((obj, _cb))
		
	def lobbyCb(self, session, event, args):
		if event == 'accepted':
			self.qLabelMsg.setText('passed')
			self.lobbyLoginGoodOrBad = 1
		if event == 'denied':
			self.lobbyLoginGoodOrBad = 2
			self.qLabelMsg.setText('failed')
		
		for cb in self.lobbyCbs:
			cb[1](cb[0], session, event, args)

	def paintHook(self, QPaintEvent):
		shade = 0.2
		if self.lobbyLoginGoodOrBad == 0:
			rgbm = (1.0, 1.0, 1.0)
		if self.lobbyLoginGoodOrBad == 1:
			rgbm = (shade, 1.0, shade)
		if self.lobbyLoginGoodOrBad == 2:
			rgbm = (1.0, shade, shade)

		w = self.wParent.size().width()
		h = self.wParent.size().height()

		painter = QtGui.QPainter(self.wParent)
		self.drawRotatingSquares(
			painter, w, h,
			w * 0.5, h * 0.25,
			100, 10, 5, self.rotiter, 20, rgbm
		)

	def drawRotatingSquares(self, painter, w, h, x, y, radius, number, bs, iter, wf, rgbm):
		pen = QtGui.QPen(QtGui.QColor(0, 0, 0))
		painter.setPen(pen)
		painter.setBrush(QtGui.QBrush(QtGui.QColor(0, 0, 0)))
		painter.setBackground(QtGui.QColor(0, 0, 0))

		# this should go somewhere else...
		qimg = self.mm.getMiniMap(self.mm_names[self.mm_dndx])
		painter.drawImage(QtCore.QRect(0, 0, w, h), qimg, QtCore.QRect(0, 0, -1, -1))

		radstep = (math.pi * 2) / number
		i = 0
		while i < number:
			a = radstep * i + iter
			b = radstep * i + iter * 1.0
			c = radstep * i + iter * 2.0
			d = radstep * i + iter * 3.0

			r = int(abs(math.cos(b) * 255.0))
			g = int(abs(math.cos(c) * 255.0))
			b = int(abs(math.sin(d) * 255.0))
			cc = g
			r = rgbm[0] * cc
			g = rgbm[1] * cc
			b = rgbm[2] * cc
			brush = QtGui.QBrush(QtGui.QColor(r, g, b))
			painter.setBrush(brush)
			r = radius - abs(math.sin(iter * 2) * wf)
			_x = math.sin(a) * r + x
			_y = math.cos(a) * r + y
			painter.drawRect(_x - bs, _y - bs, bs * 2, bs * 2)
			i = i + 1
	'''
		* create periodic event to maintain synchronous network
		* create any needed treeview items
		* create gui interface in provided parent widget
	'''
	def initFormal(self):
		#self.pParent (already set) (plug-in parent) [non-gui]
		#self.wParent (already set) (widget parent) [gui]
		self.wParent.paintHook = self.paintHook	
		self.lobby = None
		self.qTimer = QtCore.QTimer()
		self.qTimer.singleShot(200, self.update)
		'''
			Need to create login interface.
		'''
		self.qLabelMsg = QtGui.QLabel(self.wParent)
		self.qBtnLogin = QtGui.QPushButton(self.wParent)
		self.qLabelNick = QtGui.QLabel(self.wParent)
		self.qLabelPass = QtGui.QLabel(self.wParent)
		self.qFieldNick = QtGui.QLineEdit(self.wParent)
		self.qFieldPass = QtGui.QLineEdit(self.wParent)
		self.qCheckboxRemember = QtGui.QCheckBox(self.wParent)
		self.resize(self.wParent.size().width(), self.wParent.size().height())
		QtCore.QObject.connect(self.qBtnLogin, QtCore.SIGNAL('clicked()'), self.clickBtnLogin)

		self.qLabelMsg.setText('Waiting     ')
		

		#self.wParent.setStyleSheet('QWidget { background-color: black; }')		
		return

	def clickBtnLogin(self):
		if self.qBtnLogin.text() == 'Login':
			print('f')
			self.qLabelMsg.setText('Working')
			self.qBtnLogin.setText('Cancel')
			self.lobby = session.Create(self.qFieldNick.text(), self.qFieldPass.text())
			return
		if self.qBtnLogin.text() == 'Cancel':
			self.lobby = None
			self.qBtnLogin.setText('Login')
			self.qLabelMsg.setText('Waiting')
			return

	def centerWidgets(self, widgets, spacing, width, height):
		t = 0
		for w in widgets:
			t = t + w.size().width() + spacing
		offset = width * 0.5 - t * 0.5
		print('t:%s offset:%s' % (t, offset))
		for w in widgets:
			w.move(offset, height - w.size().height() * 0.5)
			offset = offset + w.size().width() + spacing
	# being human
	def resize(self, w, h):
		print(w, h)
		self.qLabelNick.setText('Nick:')
		self.qLabelPass.setText('Pass:')
		self.qFieldNick.resize(140, 20)
		self.qFieldPass.resize(140, 20)	
		self.qCheckboxRemember.setText('Remember Login?')
		#self.qBtnLogin.resize(50, 20)
		self.qBtnLogin.setText('Login')

		self.centerWidgets((self.qLabelNick, self.qFieldNick), 5, w, h * 0.5)
		self.centerWidgets((self.qLabelPass, self.qFieldPass), 5, w, h * 0.5 + 25)
		self.centerWidgets((self.qCheckboxRemember, self.qBtnLogin), 5, w, h * 0.5 + 50)

		lw = self.qLabelMsg.size().width()
		lh = self.qLabelMsg.size().height()
		self.qLabelMsg.move(w * 0.5 - lw * 0.5, h * 0.25 - lh * 0.5)
