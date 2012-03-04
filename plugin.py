'''
	Skeleton For A Plugin

	__init__ called before registration
	initFormal called when plugin can start doing stuff
	tick called
'''
class Plugin:
	def __init__(self, name, author, description, version):
		self.info_name = name
		self.info_author = author
		self.info_description = description
		self.info_version = version
		return
	def initFormal(self):
		return