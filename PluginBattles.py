import Plugin
import MapManager
from PyQt4 import QtGui
from PyQt4 import QtCore

class PluginBattles(Plugin.Plugin):
	# some debugging crap
	etypes = []

	# tracks all the battles
	battles = {}
	
	def sessionCb(self, session, event, args):
		if event not in self.etypes:
			self.etypes.append(event)
		# print(self.etypes)
		# updatebattleinfo, battleopened, joinedbattle, clientstatus, adduser
		if event == 'updatebattleinfo':
			#item = QtGui.QTreeWidgetItem();
			#item.setText(0, args[0])
			#self._MainWindow__tvnode.insertChild(0, item)
			#self.registerForMenuSelection(item)
			self.battles[args[0]] = {
				'map':				args[4],
				'playerCount':		args[1],
				'playerList':		[]
			}
			print('@@', args)
		if event == 'joinedbattle':
			self.battles[args[1]]['playerList'].append(args[0])
		if event == 'leftbattle':
			### in some cases they are not in the list i think this
			### needs to be fixed somewhere near here
			if args[0] in self.battles[args[1]]['playerList']:
				self.battles[args[1]]['playerList'].remove(args[0])
		#if event == 'battleopened':
		#	print(event, args)

	def initFormal(self):
		# initialize the network session
		self.psession = self.getPlugin('Session')
		self.psession.registerCb(self, PluginBattles.sessionCb)
		# initialize the user interface
		font = self._MainWindow__tvnode.font(0)

		font.setPointSize(10)
		
		#icon = QtGui.QIcon(r'.\images\crossed-swords.png')
		item = QtGui.QTreeWidgetItem();
		item.setText(0, 'Find Battle')
		item.setFont(0, font)
		self._MainWindow__tvnode.insertChild(0, item)
		self.registerForMenuSelection(item)
		
		#icon = QtGui.QIcon(r'.\images\animal-skull.png')
		item = QtGui.QTreeWidgetItem()
		item.setText(0, 'Current Battle')
		item.setFont(0, font)
		#item.setIcon(0, icon)
		self._MainWindow__tvnode.insertChild(0, item)
		self.registerForMenuSelection(item)
		
		self.panel = 1
		
		self.wParent.paintHook = self.paintHook
		
	def menuSelection(self, item):
		itemName = item.text(0)
		print(itemName)
		if itemName == 'Current Battle':
			self.paneltab = 1
			self.updateUI()
		if itemName == 'Find Battle':
			self.paneltab = 2
			self.updateUI()

	def resize(self):
		self.updateUI()
	
	paneltab = 0
	page = 0
	widgets = {}
	
	def widgetsDeref(self):
		for k in self.widgets:
			for w in self.widgets[k]:
				w.setParent(None)
	
	def widgetsPut(self, theType, obj):
		if theType not in self.widgets:
			self.widgets[theType] = []
		self.widgets[theType].append(obj)
	
	def widgetsGet(self, theType):
		if theType not in self.widgets:
			self.widgets[theType] = []
		ws = self.widgets[theType]
		
		for w in ws:
			if w.parent() is None:
				return w
		return None
	
	# our own local cache of QImage objects so
	# we do not just constantly create and leave
	# them to the GC.. being safe here
	mapCache = {}
	def mapCacheGet(self, mapName):
		mapMan = MapManager.getMapManager()
		if mapName in self.mapCache:
			return self.mapCache[mapName]
		qimg = mapMan.getMiniMap(mapName)
		if qimg is None:
			return None
		#qimg = QtGui.QPixmap.fromImage(qimg)
		self.mapCache[mapName] = qimg
		return qimg
	
	def paintHook(self, event):
		self.updateUI()
	
	def updateUI(self):
		# Battle Rooms
		if self.paneltab == 1:
			# current battle
			pass
		if self.paneltab == 2:
			# all battles
			panel = self.wParent
			w = panel.width()
			h = panel.height()
			
			# unattach all the widgets in the pool from their parent
			self.widgetsDeref()
			
			painter = QtGui.QPainter(panel)
			
			#w = self.widgetsGet(QtGui.QTreeWidgetItem)
			#print(w)
			
			colcnt = int(w / 100)
			rowcnt = int(h / 100)
			if colcnt < 1:
				colcnt = 1
			if rowcnt < 1:
				rowcnt = 1
				
			print('colcnt/rowcnt', colcnt, rowcnt)
			
			
			# battles
			bc = 0
			sz = colcnt * rowcnt
			off = self.page * (colcnt * rowcnt)
			for bk in self.battles:
				b = self.battles[bk]
				if bc >= (off + sz):
					# too far skip out
					break
				if bc >= off:
					andx = bc - off					# actual index (relative to page)
					arow = int(andx / colcnt)		# actual row
					acol = andx - (arow * colcnt)	# actual col
					ax = acol * 100					# actual x (col)
					ay = arow * 100					# actual y (row)
					# okay render this to the panel
					mapImage = self.mapCacheGet(b['map'])
					if mapImage is not None:
						#print('***found***', b['map'], ax, ay)
						#label = self.widgetsGet('label')
						#if label is None:
						#	label = QtGui.QLabel()
						#	self.widgetsPut('label', label)
						#label.setPixmap(mapImage)
						#label.move(ax, ay)
						#label.resize(100, 100)
						#label.setParent(panel)
						#label.setText('test')
						painter.drawImage(
											QtCore.QRect(ax, ay, 100, 100), 
											mapImage, 
											QtCore.QRect(0, 0, -1, -1)
						)
				bc = bc + 1
			
		
			# My Current Battle
			# Show All Battles
		
		# all battles display
			# ---------------------------------------------
			# reserve upper portion for search controls
			# ---------------------------------------------
			# need to be able to create a grid and for each
			# grid cell the battle's map is displayed along
			# with some battle information underneath it
			#      also on side have buttons to see next page because
			#      all the battles are not likely to fit onto a single
			#      page
		# current battle display (if we are currently in a battle room)
			# battle chat box in upper left
			# chat box entry text 
			# user list on right using treeview likely
			# map image in bottom right
			# bottom panel has button to rejoin/join/start battle
		pass
		
	def resize(self, w, h):
		pass
