import plugin

class pluginBattles(plugin.Plugin):
	etypes = []

	def sessionCb(self, session, event, args):
		if event not in self.etypes:
			self.etypes.append(event)
		# print(self.etypes)
		# updatebattleinfo, battleopened, joinedbattle, clientstatus, adduser
		if event == 'updatebattleinfo':
			print(event, args)
		if event == 'joinedbattle':
			print(event, args)
		if event == 'battleopened':
			print(event, args)

	def initFormal(self):
		self.psession = self.getPlugin('Session')
		self.psession.registerCb(self, pluginBattles.sessionCb)
		
	def resize(self, w, h):
		pass
