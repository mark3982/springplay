import Plugin
import MapManager
from PyQt4 import QtGui
from PyQt4 import QtCore

class PluginBattles(Plugin.Plugin):
	# some debugging crap
	etypes = []

	# tracks all the battles
	battles = {}
	
	mapsUpdated = False
	
	def sessionCb(self, session, event, args):
		if event == 'battleopened':
			args['playerCount'] = 0
			args['playerList'] = []
			self.battles[args['id']] = args
		if event == 'updatebattleinfo':
			self.battles[args['id']]['map'] = args['map']
			self.battles[args['id']]['playerCount'] = args['playerCount']
			return
		if event == 'joinedbattle':
			self.battles[args['id']]['playerList'].append(args['user'])
			return
		if event == 'leftbattle':
			if args['id'] not in self.battles:
				return
			if args['user'] in self.battles[args['id']]['playerList']:
				self.battles[args['id']]['playerList'].remove(args['user'])
			return
		return

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
		
		self.qTimer = QtCore.QTimer()
		self.qTimer.singleShot(1000, self.checkForForceRedraw)
		return
	
	#
	# If the asynchronous callback for a MapManager URL
	# fetch has been executed the mapsUpdated will be 
	# set to True and we shall cause a paint event to
	# happen which should redraw any missing images.
	#
	def checkForForceRedraw(self):
		if mapsUpdated:
			self.wParent.repaint()
		
	def menuSelection(self, item):
		itemName = item.text(0)
		print(itemName)
		if itemName == 'Current Battle':
			self.paneltab = 1
			self.wParent.repaint()
		if itemName == 'Find Battle':
			self.paneltab = 2
			self.wParent.repaint()

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
		
	def mapFetchAsyncCb(self, mapName):
		# this is actually called from another
		# thread so I am not sure how thread
		# safe it is, but if problems arise this
		# is likely the culprit
		self.mapsUpdated = True
	
	def updateUI(self):
		# Battle Rooms
		if self.paneltab == 1:
			# current battle
			return
		if self.paneltab == 2:
			# all battles
			panel = self.wParent
			w = panel.width()
			h = panel.height()
			
			# this is set by a callback from the MapManager module
			# when a asynchronous URL fetch is done to get the
			# minimap image, or anything else and we need to redraw
			self.mapsUpdated = False 
			
			# unattach all the widgets in the pool from their parent
			self.widgetsDeref()
			
			painter = QtGui.QPainter(panel)
			fontm = painter.fontMetrics()
			
			#w = self.widgetsGet(QtGui.QTreeWidgetItem)
			#print(w)
			
			gridw = 400
			gridh = 100
			colcnt = int(w / gridw)
			rowcnt = int(h / gridh) + 1
			
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
					ax = acol * gridw				# actual x (col)
					ay = arow * gridh				# actual y (row)
					# okay render this to the panel
					#mapImage = self.mapCacheGet(b['map'])
					mapImage = MapManager.fetchMiniMapAsync(b['map'], self.mapFetchAsyncCb)
					if mapImage is not None:
						painter.drawImage(
											QtCore.QRect(ax, ay, 100, 100), 
											mapImage, 
											QtCore.QRect(0, 0, -1, -1)
						)
					if acol == colcnt - 1:
						tw = w - ax
					else:
						tw = gridw
					painter.drawRect(ax, ay, tw, gridh)
					painter.drawText(ax + 110, ay + fontm.height() * 0 + 10, b['mod'])
					painter.drawText(ax + 110, ay + fontm.height() * 1 + 10, b['desc'])
					painter.drawText(ax + 110, ay + fontm.height() * 2 + 10, b['map'])
				bc = bc + 1
			return
		return
		
	def resize(self, w, h):
		return
