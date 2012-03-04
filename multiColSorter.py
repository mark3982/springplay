class MultiColSorter:
	ORDER_ASC = 	0x01
	ORDER_DEC = 	0x02
	ORDER_CNT = 	0x04			# need to implement
	ORDER_NOCASE = 	0x10
	ORDER_NATURAL = 0x03

	def __init__(self):
		self.rows = []
		self.sortw = []
		self.mrc = 0
	def addRow(self, items):
		self.rows.append(items)
	def getRows(self):
		return self.rows
	'''
		Applies each sort individualy to the results.
	'''
	def doSort(self):
		rows = self.rows
		sortw = self.sortw
		_n = []
		_n.append(rows.pop(0))
		while len(rows) > 0:
			r = rows.pop(0)
			x = 0
			while x < len(_n):
				g = _n[x]
				if self.doGre(sortw, r, g):
					break
				x = x + 1
			_n.insert(x, r)
		self.rows = _n
		return

	def doGre(self, sortw, a, b):
		x = 0
		while x < len(sortw):
			w = sortw[x]
			if w[1] == 3:
				continue
			_a = a[w[0]]
			_b = b[w[0]]
			if w[1] & self.ORDER_NOCASE:
				_a = _a.lower()
				_b = _b.lower()
			if w[1] & self.ORDER_DEC:
				if _a > _b:
					return True
				if _a == _b:
					x = x + 1
					continue
			if w[1] & self.ORDER_ASC:
				if _a < _b:
					return True
				if _a == _b:
					x = x + 1
					continue	
			return False
		return False
		
	'''
		Sorts the rows by the column using the type as the method 
		to sort. Multiple calls are stacked and sorts are performed
		using a priority type method. 

		mod, plyrcnt

		type:
			1 = ascending
			2 = descending
			3 = natural (no-sort)
	'''
	def addSort(self, colndx, type):
		_n = []
		_n.append((colndx, type))
		for w in self.sortw:
			if w[0] != colndx:
				_n.append(w)
		self.sortw = _n
