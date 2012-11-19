from PyQt4 import QtGui
from PyQt4 import QtCore
import sys

class QTest(QtGui.QWidget):
	def paintEvent(self, event):
		w = self.size().width()
		h = self.size().height()
		painter = QtGui.QPainter(self)
		painter.drawImage(
			QtCore.QRect(0, 0, w, h),
			self.i,
			QtCore.QRect(0, 0, -1, -1)
		)

app = QtGui.QApplication(sys.argv)

w = QTest()
w.resize(200, 200)
w.move(0, 0)
w.setWindowTitle('none')
w.show()

iw = 100
ih = 100
w.i = QtGui.QImage(iw, ih, QtGui.QImage.Format_RGB16) 

i = 0
while i < (iw * ih):
	# notice 0x1f produces dark blue and 0xff bright blue
	# 0x1f would be RGB16(565 Format), and 0xff RGB32(888 Format)
	c = 0x1f
	w.i.setPixel(i - (int(i / iw) * iw), int(i / iw), c)
	i = i + 1
sys.exit(app.exec_())