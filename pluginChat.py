import plugin

class pluginChat(plugin.Plugin):
	def sessionCb(self, session, event, args):
		pass

	def initFormal(self):
		self.psession = self.getPlugin('Session')
		self.psession.registerCb(self, pluginChat.sessionCb)
		
	def resize(self, w, h):
		pass
