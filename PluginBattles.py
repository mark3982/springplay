import Plugin
import MapManager
from PyQt4 import QtGui
from PyQt4 import QtCore

def toBinary(val):
	val = int(val)
	b = ''
	n = 1
	c = 0
	while c < 32:
		if val & n > 0:
			b = '1%s' % b
		else:
			b = '0%s' % b
		n = n << 1
		c = c + 1
	return b

class PluginBattles(Plugin.Plugin):
	# some debugging crap
	etypes = []

	# tracks all the battles
	battles = {}
	players = {}
	
	mapsUpdated = False
	
	image_cache = {}
	
	def sessionCb(self, session, event, args):
		if event == 'battleopened':
			args['players'] = []
			args['specs'] = 0
			self.battles[args['id']] = args
			self.mapsUpdated = True
			return
		if event == 'updatebattleinfo':
			self.battles[args['id']]['map'] = args['map']
			self.battles[args['id']]['hash'] = args['hash']
			self.battles[args['id']]['hasPass'] = args['hasPass']
			self.battles[args['id']]['specs'] = args['specs']
			self.mapsUpdated = True
			return
		if event == 'joinedbattle':
			self.battles[args['id']]['players'].append(args['user'])
			self.mapsUpdated = True
			return
		if event == 'clientstatus':
			self.players[args['user']] = args
			return
		if event == 'leftbattle':
			if args['id'] not in self.battles:
				return
			if args['user'] in self.battles[args['id']]['players']:
				self.battles[args['id']]['players'].remove(args['user'])
			self.mapsUpdated = True
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
		self.sbpixel = 0
		
		self.wParent.paintHook = self.paintHook
		
		self.qTimer = QtCore.QTimer()
		self.qTimer.singleShot(1000, self.checkForForceRedraw)
		
		self.image_cache = {}
		
		# set the background color
		#pal = self.wParent.palette()
		#pal.setColor(QtGui.QPalette.Window, QtGui.QColor(0xff, 0xff, 0xff))
		#self.wParent.setPalette(pal)
		#self.wParent.setAutoFillBackground(True)
		return
	
	#
	# If the asynchronous callback for a MapManager URL
	# fetch has been executed the mapsUpdated will be 
	# set to True and we shall cause a paint event to
	# happen which should redraw any missing images.
	#
	def checkForForceRedraw(self):
		self.qTimer.singleShot(1000, self.checkForForceRedraw)
		if self.mapsUpdated:
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
	
	def sbValueChanged(self):
		self.sbpixel = self.widgets['bs_scroll'].value()
		self.wParent.repaint()
		return
	
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
			
			painter = QtGui.QPainter(panel)
			painter.setFont(QtGui.QFont('Tahoma'))
			fontm = painter.fontMetrics()
			
			# create options
			# - option for show empty
			# - option for show full
			# - option for official games
			# - search box for game description
			# - button to open new battle
			
			# clear any controls from the other panel
			widgets = self.widgets
			
			for k in widgets:
				if k.find('bs_') != 0:
					w = widgets[k]
					# unref it from the wid
					w.setParent(None)
					widgets[k] = None
			
			# basically we create them like this so we can easily
			# clear them if they switch to the current battle panel
			if 'bs_scroll' not in widgets:
				widgets['bs_scroll'] = QtGui.QScrollBar(panel)
				widgets['bs_scroll'].valueChanged.connect(self.sbValueChanged)
				
			bs_scroll = widgets['bs_scroll']
			bs_scroll.move(panel.width() - 15, 50)
			bs_scroll.resize(15, panel.height() - 50)
			bs_scroll.show()
			
			
			if 'bs_spanel' not in widgets:
				bs_spanel = QtGui.QWidget(panel)
				bs_bl = QtGui.QHBoxLayout()
				
				widgets['bs_spanel'] = bs_spanel
				
				bs_spanel.move(0, 0)
				bs_spanel.resize(panel.rect().width(), 50)
				bs_spanel.setLayout(bs_bl)
				bs_spanel.show()
			
				widgets['bs_newbattle'] = QtGui.QPushButton(panel)
				widgets['bs_newbattle'].setText('New Battle')
				widgets['bs_newbattle'].show()
				bs_bl.addWidget(widgets['bs_newbattle'])
				
				
				widgets['bs_showempty'] = QtGui.QCheckBox(panel)
				widgets['bs_showempty'].setText('Show Empty')
				widgets['bs_showempty'].show()
				bs_bl.addWidget(widgets['bs_showempty'])

				widgets['bs_showfull'] = QtGui.QCheckBox(panel)
				widgets['bs_showfull'].setText('Show Full')
				widgets['bs_showfull'].show()
				bs_bl.addWidget(widgets['bs_showfull'])
				
				widgets['bs_nextpage'] = QtGui.QPushButton(panel)
				widgets['bs_nextpage'].setText('Next Page')
				widgets['bs_nextpage'].show()
				bs_bl.addWidget(widgets['bs_nextpage'])
				
				widgets['bs_prevpage'] = QtGui.QPushButton(panel)
				widgets['bs_prevpage'].setText('Prev Page')
				widgets['bs_prevpage'].show()
				bs_bl.addWidget(widgets['bs_prevpage'])
			
			gyoff = 50
			
			gridw = 400
			gridh = 100
			colcnt = int(w / gridw)
			rowcnt = int(h / (gridh - gyoff)) + 1
			
			
			widgets['bs_scroll'].setRange(0, rowcnt * gridh)
			
			if 'battleimg' not in self.image_cache:
				self.image_cache['battleimg'] = QtGui.QImage('./images/surprised-skull-2.png')
			
			if colcnt < 1:
				colcnt = 1
			if rowcnt < 1:
				rowcnt = 1	
			
			# battles
			bc = 0
			sz = colcnt * rowcnt
			off = self.page * (colcnt * rowcnt)
			for bk in self.battles:
				b = self.battles[bk]

				#andx = bc - off					# actual index (relative to page)
				andx = bc
				bc = bc + 1
				
				arow = int(andx / colcnt)		# actual row
				acol = andx - (arow * colcnt)	# actual col
				ax = acol * gridw				# actual x (col)
				ay = arow * gridh				# actual y (row)
				
				# above the top
				if ay + gridh < self.sbpixel:	
					continue
				# past the bottom
				if ay > (self.sbpixel + h):
					continue
				# adjust for slider position
				ay = ay - self.sbpixel
				
				# okay render this to the panel
				#mapImage = self.mapCacheGet(b['map'])
				mapImage = MapManager.fetchMiniMapAsync(b['map'], self.mapFetchAsyncCb)
				if mapImage is not None:
					painter.drawImage(
										QtCore.QRect(ax, ay + gyoff, 100, 100), 
										mapImage, 
										QtCore.QRect(0, 0, -1, -1)
					)
				for p in b['players']:
					if p in self.players:
						if self.players[p]['inGame']:
							painter.drawImage(
												QtCore.QRect(ax, ay + gyoff, 100, 100), 
												self.image_cache['battleimg'], 
												QtCore.QRect(0, 0, -1, -1)
							)
							break
				#########################
				if acol == colcnt - 1:
					tw = w - ax
				else:
					tw = gridw
				painter.drawRect(ax, ay + gyoff, tw, gridh)
				painter.drawText(ax + 110, gyoff + ay + fontm.height() * 0 + 10, 'Mod: %s' % b['mod'])
				painter.drawText(ax + 110, gyoff + ay + fontm.height() * 1 + 10, 'Desc: %s' % b['desc'])
				painter.drawText(ax + 110, gyoff + ay + fontm.height() * 2 + 10, 'Map: %s' % b['map'])
				painter.drawText(ax + 110, gyoff + ay + fontm.height() * 3 + 10, 'Players/Specs: %s/%s' % (len(b['players']) - b['specs'], b['specs']))
				
				####################################
				
				cntSpecs = b['specs'] 
				cntInGame = 0
				for p in b['players']:
					if p in self.players:
						if self.players[p]['inGame']:
							cntInGame = cntInGame + 1
				cntIdle = len(b['players']) - cntInGame - cntSpecs
				
				maxp = b['maxPlayers']
				
				perRow = 20
				
				c_InGame = QtGui.QColor(0x00, 0xff, 0x00)
				c_Spec = QtGui.QColor(0x00, 0xff, 0xff)
				c_Idle = QtGui.QColor(0x00, 0x00, 0x00)
				c_Empty = QtGui.QColor(0x99, 0x99, 0x99)
				
				i = 0
				while i < maxp:
					row = int(i / perRow)
					col = i - (row * perRow)
					__y = row * 10 + ay + fontm.height() * 4 + 10 + gyoff
					__x = col * 10 + ax + 110
					
					if cntInGame > 0:
						cntInGame = cntInGame - 1
						c = c_InGame
					elif cntSpecs > 0:
						cntSpecs = cntSpecs - 1
						c = c_Spec
					elif cntIdle > 0:
						cntIdle = cntIdle - 1
						c = c_Idle
					else:
						c = c_Empty
						
					painter.fillRect(__x, __y, 7, 7, c)
					
					i = i + 1
				#####################
				continue
				#####################
			return
		return
		
	def resize(self, w, h):
		return
