import Plugin

class PluginChat(Plugin.Plugin):
	def sessionCb(self, session, event, args):
		pass

	def initFormal(self):
		self.psession = self.getPlugin('Session')
		self.psession.registerCb(self, PluginChat.sessionCb)
		
	def resize(self, w, h):
		pass
