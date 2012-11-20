import Plugin
from PyQt4 import QtGui
from PyQt4 import QtCore

class PluginBattles(Plugin.Plugin):
	etypes = []

	def sessionCb(self, session, event, args):
		if event not in self.etypes:
			self.etypes.append(event)
		# print(self.etypes)
		# updatebattleinfo, battleopened, joinedbattle, clientstatus, adduser
		if event == 'updatebattleinfo':
			item = QtGui.QTreeWidgetItem();
			item.setText(0, args[0])
			self._MainWindow__tvnode.insertChild(0, item)
			self.registerForMenuSelection(item)
		if event == 'joinedbattle':
			print(event, args)
		if event == 'battleopened':
			print(event, args)

	def initFormal(self):
		# initialize the network session
		self.psession = self.getPlugin('Session')
		self.psession.registerCb(self, PluginBattles.sessionCb)
		# initialize the user interface
		item = QtGui.QTreeWidgetItem();
		item.setText(0, 'test')
		self._MainWindow__tvnode.insertChild(0, item)
		self.registerForMenuSelection(item)
		
	def menuSelection(self, item):
		print(item.text(0))
	
	def updateUI(self):
		# create a sub-node on the left tree view for each battle and also
		# make a little picture for it's icon
		# .....
		# now keep track of which battle is selected and display it's information
		# on the right side like the map, the players, ...ect
		# ....
		# also if battle is select that we are in then display the battle UI which 
		# includes a chat window
		pass
		
	def resize(self, w, h):
		pass
