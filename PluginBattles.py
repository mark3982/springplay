import Plugin
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
		if event == 'joinedbattle':
			self.battles[args[1]]['playerList'].append(args[0])
		if event == 'leftbattle':
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
		
		item = QtGui.QTreeWidgetItem();
		item.setText(0, 'Find Battle')
		item.setFont(0, font)
		self._MainWindow__tvnode.insertChild(0, item)
		self.registerForMenuSelection(item)
		
		item = QtGui.QTreeWidgetItem()
		item.setText(0, 'Current Battle')
		item.setFont(0, font)
		self._MainWindow__tvnode.insertChild(0, item)
		self.registerForMenuSelection(item)
		
	def menuSelection(self, item):
		print(item.text(0))
	
	def updateUI(self):
		# Battle Rooms
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
