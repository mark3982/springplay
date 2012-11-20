'''
	Skeleton For A Plugin

	__init__ called before registration
	initFormal called when plugin can start doing stuff
	tick called
'''
class Plugin:
	def __init__(self, name, author, description, version, gplugins):
		self.info_name = name
		self.info_author = author
		self.info_description = description
		self.info_version = version
		self.gplugins = gplugins
		return
	def initFormal(self):
		return
	def getPlugin(self, name):
		for plugin in self.gplugins:
			if plugin.info_name == name:
				return plugin
		return None
	def menuSelection(self, item):
		pass
	def registerForMenuSelection(self, item):
		self._MainWindow__tvhandler.append(item)
