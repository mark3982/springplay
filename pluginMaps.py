import plugin

class pluginMaps(plugin.Plugin):
	'''
		Determine if we have an utility to handle sd7 archives.
			If not demand focus and prompt for it.
		Determine if we have any new maps not yet processed.
			If so demand focus and display progress.
	'''
	def initFormal(self):
		#plugin.Plugin.__init__(self, name, author, description, version)
		#self.mm = mapManager.mapManager()
		#self.mm_names = self.mm.getMapNames()
		#qimg = self.mm.getMiniMap(self.mm_names[self.mm_dndx])
		pass
	
	def resize(self, width, height):
		pass
