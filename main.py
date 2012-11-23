import version
import sys
import os
import hashlib
import time
import gui
import random
import math
import subprocess
from PyQt4 import QtGui
from PyQt4 import QtCore

import struct
import Session
import sys
import os
import zipfile
import time
from ctypes import *
import math

import PluginSession
import PluginChat
import PluginMaps
import PluginBattles

VERSION = 'SpringPlay-%s-A' % (version.getVersionString())
print(VERSION)

gPlugins = []
def regPlugin(plugin):
	gPlugins.append(plugin)	
	
'''
	* register the plugins
	* create the user interface
	* formaly initialize plugins
	* display plugins in treeview
	* select default plugin to display
'''
regPlugin(PluginSession.PluginSession(
	'Session', 'Leonard Kevin McGuire Jr', 
	'Manages network connection to the lobby server.',
	'builtin-%s' % (VERSION),
	'Login',
	gPlugins
))
regPlugin(PluginChat.PluginChat(
	'Chat', 'Leonard Kevin McGuire Jr',
	'Manages chat channels.',
	'builtin-%s' % (VERSION),
	'Chat Rooms',
	gPlugins
))
regPlugin(PluginBattles.PluginBattles(
	'Battles', 'Leonard Kevin McGuire Jr',
	'Management Of Battles',
	'builtin-%s' % (VERSION),
	'Battles',
	gPlugins
))
regPlugin(PluginMaps.PluginMaps(
	'Maps', 'Leonard Kevin McGuire Jr',
	'Management of maps',
	'builtin-%s' % (VERSION),
	'Maps',
	gPlugins
))


class QWidgetEx(QtGui.QWidget):
	paintHook = None
	def paintEvent(self, event):
		QtGui.QWidget.paintEvent(self, event)
		if self.paintHook is not None:
			self.paintHook(event)


class MainWindow(QtGui.QWidget):
	'''
		* create widgets
		* formally initialize plugins
		* create widget for each plugin

		__tvnodes holds all treeview nodes associated with this plug-in, while
		__tvnode holds the root level treeview node for the plug-in, i used the
		__tvnodes to make it easier to write code since i check if it is in it
		__tvnodes always contains __tvnode and any others

		startupwork, holds plugins that need to do work that is either going to
		inconvience the user through confusion when it locks the interface up
		trying to do it... the current case is the map plugin needs to scan down
		all the installed maps and extract needed information from them
	'''
	def __init__(self):
		QtGui.QWidget.__init__(self)
	
		self.formalized = False

		# app-icon = 	blade-bite.png
		# battle = all-for-one.png
		# 			current battle = animal-skull.png
		#           all battles = crossed-swords.png
		# session = anatomy.png / auto-repair.png
		icon = QtGui.QIcon(r'.\images\blade-bite.png')
		self.setWindowIcon(icon)
		
		font = QtGui.QFont('Monospace', 12)
		
		self.wTreeView = QtGui.QTreeWidget(self)
		self.wTreeView.setHeaderHidden(True)
		self.wTreeView.show()
		self.activePlug = None
		QtCore.QObject.connect(self.wTreeView, QtCore.SIGNAL('itemSelectionChanged()'), self.treeViewSelectionChanged)

		for plug in gPlugins:
			pWidget = QWidgetEx(self)
			plug.pParent = self			# plugin parent
			plug.wParent = pWidget		# widget parent
			plug.__tvnode = QtGui.QTreeWidgetItem()
			plug.__tvnode.setFont(0, font)
			plug.__tvnode.setText(0, plug.menuText)
			plug.__tvnodes = [plug.__tvnode]
			plug.__tvhandler = []
			plug.initFormal()
			self.wTreeView.insertTopLevelItems(0, [plug.__tvnode])
			plug.wParent.hide()

		self.formalized = True
	'''
		* resize all widgets

		Interesting.. bugger here. Do not call widget.resize(...) then expect
		to access widget.size() members and have them match. Apparently, some
		processing must take place before it will properly update. And, of
		course that is the least efficent way to do it, but now I know.
	'''
	def resizeEvent(self, event):
		mnuWidth = 150
	
		h = event.size().height()
		w = event.size().width()
		self.wTreeView.resize(mnuWidth, h)
		self.wTreeView.move(0, 0)
		if self.formalized:
			for plug in gPlugins:
				widget = plug.wParent
				widget.move(mnuWidth, 0)
				widget.resize(w - mnuWidth, h)
				plug.resize(w - mnuWidth, h)

	'''
		Hide the widget currently being shown, and show the
		widget associated with the plug-in that has just been
		newly selected.
	'''
	def treeViewSelectionChanged(self):
		sitem = self.wTreeView.selectedItems()[0]
		oitem = sitem
		# this will transverse down onto the root node
		# and thus allow us to determine what plugin this
		# sub-node belongs to and of course to display the
		# plugin panel
		while sitem.parent() is not None:
			sitem = sitem.parent()
		
		for plug in gPlugins:
			# lets the plugin register a handler for
			# a specific item in the treeview normally it
			# will be for items it has added
			if oitem in plug.__tvhandler:
				plug.menuSelection(oitem)
			# causes the plugin to display in the right
			# part of the main window when it's treeview
			# item is selected which is represented by
			# plug.__tvnode and also inside of plug.__tvnodes
			# since plug.__tvnodes.append(plug.__tvnode) should
			# always have happened
			if sitem in plug.__tvnodes:
				if self.activePlug != plug:
					if self.activePlug is not None:
						self.activePlug.wParent.hide()
					self.activePlug = plug
					plug.wParent.show()
					plug.resize(plug.wParent.size().width(), plug.wParent.size().height())
	
		
def main():
	app = QtGui.QApplication(sys.argv)
	# Cleanlooks
	# Plastique
	# Motfif
	# CDE
	style = QtGui.QStyleFactory.create('Plastique')
	app.setStyle(style)

	print(QtGui.QStyleFactory.keys())

	w = MainWindow()
	w.resize(600, 480)
	w.move(400, 400)
	w.setWindowTitle(VERSION)
	w.show()

	'''
	t = QtGui.QTreeWidget(w)
	t.resize(400, 400)
	t.move(0, 0)
	t.setColumnCount(1)

	ti = QtGui.QTreeWidgetItem()
	tm = QtGui.QTreeWidgetItem()
	tm.setText(0, 'Configuration')
	ti.setText(0, 'Session')
	ti.addChild(tm)

	t.insertTopLevelItems(0, [ti])
	t.show()
	'''
	
	sys.exit(app.exec_())

main()



