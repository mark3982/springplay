'''
	Handles the GUI functions for the platform.


	Copied From:
		Was in hurry and this works.
		http://code.activestate.com/recipes/208699-calling-windows-api-using-ctypes-and-win32con/


	BUT... I spent many hours realizing I am running in 64-bit mode.. Oh, damn. You know what I had
	to finally go back and fix my structure. This article helped a lot, lol:
	http://msdn.microsoft.com/en-us/library/aa384242(v=vs.85).aspx

	Any kind of HANDLE is platform processor word size. So, c_void_p it. Not sure if c_longlong is
	processor word size in 32-bit mode. So, just went with c_void_p because I know it will change
	correctly. Also, LPARAM and WPARAM... they changed.

'''
import win32con
import sys
from ctypes import *
from ctypes.wintypes import HWND, WPARAM, LPARAM, UINT

WNDPROC = WINFUNCTYPE(c_longlong, HWND, UINT, WPARAM, LPARAM)

class WNDCLASSEX(Structure): 
    _fields_ = [("cbSize", c_uint), 
                ("style", c_uint), 
                ("lpfnWndProc", WNDPROC), 
                ("cbClsExtra", c_int), 
                ("cbWndExtra", c_int), 
                ("hInstance", c_void_p), 
                ("hIcon", c_void_p), 
                ("hCursor", c_void_p), 
                ("hBrush", c_void_p), 
                ("lpszMenuName", c_char_p), 
                ("lpszClassName", c_char_p), 
                ("hIconSm", c_void_p)] 

class WNDCLASS(Structure):
	_fields_ = [('style', c_uint),
				('lpfnWndProc', WNDPROC),
				('cbClsExtra', c_int),
				('cbWndExtra', c_int),
				('hInstance', c_void_p),
				('hIcon', c_void_p),
				('hCursor', c_void_p),
				('hbrBackground', c_void_p),
				('lpszMenuName', c_char_p),
				('lpszClassName', c_char_p)]

class RECT(Structure):
	_fields_ = [('left', c_long),
				('top', c_long),
				('right', c_long),
				('bottom', c_long)]

class PAINTSTRUCT(Structure):
	_fields_ = [('hdc', c_void_p),
				('fErase', c_int),
				('rcPaint', RECT),
				('fRestore', c_int),
				('fIncUpdate', c_int),
				('rgbReserved', c_char * 32)]

class POINT(Structure):
	_fields_ = [('x', c_long),
				('y', c_long)]
	
class MSG(Structure):
	_fields_ = [('hwnd', c_void_p),
				('message', c_uint),
				('wParam', c_void_p),
				('lParam', c_void_p),
				('time', c_int),
				('pt', POINT)]

class ABC(Structure):
	_fields_ = [
		('a', c_int),
		('b', c_uint),
		('c', c_int)
	]

class TITLEBARINFO(Structure):
	_fields_ = [
		('cbSize', c_uint),
		('rcTitleBar', RECT),
		('rgstate0', c_uint),
		('rgstate1', c_uint),
		('rgstate2', c_uint),
		('rgstate3', c_uint),
		('rgstate4', c_uint),
		('rgstate5', c_uint),
	]

class TEXTMETRIC(Structure):
	_fields_ = [
		('tmHeight', c_long),
		('tmAscent', c_long),
		('tmDescent', c_long),
		('tmInternalLeading', c_long),
		('tmExternalLeading', c_long),
		('tmAveCharWidth', c_long),
		('tmMaxCharWidth', c_long),
		('tmWeight', c_long),
		('tmOverhang', c_long),
		('tmDigitizedAspectX', c_long),
		('tmDigitizedAspectY', c_long),
		('tmFirstChar', c_char),
		('tmLastChar', c_char),
		('tmDefaultChar', c_char),
		('tmBreakChar', c_char),
		('tmItalic', c_char),
		('tmUnderlined', c_char),
		('tmStruckOut', c_char),
		('tmPitchAndFamily', c_char),
		('tmCharSet', c_char)
	]

'''
'''
gCoData = None
gConf = {
	'fontHeight':	None,
	'fontWidth':	None,
	'fontSize':		None,
	'colCnt':		None,
	'rowCnt':		None,
	'initCb':		None,
	'tickCb':		None,
	'keyCb':		None,
	'clickCb':		None,
	'hfont':		None,
}


def MainWin(fontSize, colCnt, rowCnt, initCb, tickCb, keyCb, clickCb):
	global gConf, gCoData

	gConf['fontSize'] = fontSize
	gConf['colCnt'] = colCnt
	gConf['rowCnt'] = rowCnt
	gConf['initCb'] = initCb
	gConf['tickCb'] = tickCb
	gConf['keyCb'] = keyCb
	gConf['clickCb'] = clickCb
	gCoData = [(' ', 0, 0, None)] * (colCnt * rowCnt)

	Write(10, 10, 'hello', 0x0ff, 0x0ff00)
	Write(9, 11, 'hello', 0x0ff, 0x05577dd)

	#GetLastError = windll.kernel32.GetLastError	
	# Define Window Class
	wndclass = WNDCLASSEX()
	wndclass.cbSize = sizeof(WNDCLASSEX)
	wndclass.style = win32con.CS_HREDRAW | win32con.CS_VREDRAW
	wndclass.lpfnWndProc = WNDPROC(WndProc)
	wndclass.cbClsExtra = 0
	wndclass.cbWndExtra = 0
	wndclass.hInstance = windll.kernel32.GetModuleHandleA(c_int(0))
	wndclass.hIcon = windll.user32.LoadIconA(c_int(0), c_int(win32con.IDI_APPLICATION))
	wndclass.hCursor = windll.user32.LoadCursorA(c_int(0), c_int(win32con.IDC_ARROW))
	wndclass.hBrush = windll.gdi32.GetStockObject(c_int(win32con.BLACK_BRUSH))
	wndclass.hIconSm = windll.user32.LoadIconA(c_int(0), c_int(win32con.IDI_APPLICATION))
	wndclass.hbrBackground = windll.gdi32.GetStockObject(c_int(win32con.WHITE_BRUSH))
	wndclass.lpszMenuName = 0
	wndclass.lpszClassName = b'winClassMain'
	# Register Window Class
	windll.user32.RegisterClassExA(byref(wndclass))
	# Create Window
	hwnd = windll.user32.CreateWindowExA(0,
						  wndclass.lpszClassName,
						  b'SpringPlay',
						  0x100, #win32con.WS_OVERLAPPEDWINDOW,
						  win32con.CW_USEDEFAULT,
						  win32con.CW_USEDEFAULT,
						  700,
						  700,
						  0,
						  0,
						  wndclass.hInstance,
						  0)
	if hwnd == 0:
		exit()
	# Show Window
	windll.user32.ShowWindow(c_int(hwnd), c_int(win32con.SW_SHOWNORMAL))
	windll.user32.UpdateWindow(c_int(hwnd))

	# Pump Messages
	msg = MSG()
	NULL = c_int(0)

	windll.user32.SetTimer(c_int(hwnd), c_int(0), c_int(50), 0)
	
	'''
		Go ahead and get font width and height.
	'''
	hfont = windll.gdi32.CreateFontA(
		gConf['fontSize'], 0, 0, 0, win32con.FW_DONTCARE, 0, 0, 0, 
		win32con.DEFAULT_CHARSET, win32con.OUT_OUTLINE_PRECIS,
		win32con.CLIP_DEFAULT_PRECIS, win32con.CLEARTYPE_QUALITY, 
		win32con.VARIABLE_PITCH, b'Consolas'
	)

	textMetric = TEXTMETRIC()
	abc = ABC()
	hdc = windll.user32.GetDC(c_void_p(hwnd))
	windll.gdi32.SelectObject(c_void_p(hdc), hfont)
	windll.gdi32.GetTextMetricsA(c_void_p(hdc), byref(textMetric)) 
	windll.gdi32.GetCharABCWidthsA(c_void_p(hdc), 0, 0, byref(abc))
	#windll.gdi32.TextOutA(c_int(hdc), 10, 10, b'A', 1)

	gConf['hfont'] = hfont
	gConf['fontHeight'] = fontSize
	gConf['fontWidth'] = abc.a + abc.b + abc.c   # 8

	tbi = TITLEBARINFO()
	tbi.cbSize = sizeof(TITLEBARINFO)

	windll.user32.GetTitleBarInfo(c_void_p(hwnd), byref(tbi))

	rect = tbi.rcTitleBar

	windll.user32.SetWindowPos(
				c_void_p(hwnd), 0, 
				c_int(0), c_int(0), 
					c_int(gConf['fontWidth'] * gConf['colCnt']), 
					c_int(gConf['fontHeight'] * gConf['rowCnt'] + (rect.bottom - rect.top) + 7),
				c_int(0)
	)   

	initCb()

	DispatchMessageA = windll.user32.DispatchMessageA
	DispatchMessageA.argtypes = [c_void_p]
	TranslateMessage = windll.user32.TranslateMessage
	TranslateMessage.argtypes = [c_void_p]
	GetMessageA = windll.user32.GetMessageA
	GetMessageA.argtypes = [c_void_p, c_int, c_int, c_int]

	while GetMessageA(byref(msg), c_int(0), c_int(0), c_int(0)) != 0:
		TranslateMessage(byref(msg))
		DispatchMessageA(byref(msg))

	return msg.wParam
	
'''
	This handles all the platform specific stuff. It also allows our platform independant code to
	work by calling a callback provided to this module's initialization function. This basically
	just provides an elaborate console with support for images and high colors.

	I figure doing the same on the unix platform with X11 will be the solution, or maybe just using
	an actual console (maybe preferable - but color limitations can exist then). I am not sure yet.
'''
def Write(x, y, txt, fg, bg, tag = None):
	global gConf, gCoData
	colCnt = gConf['colCnt']
	for c in txt:
		gCoData[y * colCnt + x] = (c, fg, bg, tag)
		x = x + 1
def WriteAr(x, y, out):
	for o in out:
		if len(o) > 3:
			tag = o[3]
		else:
			tag = None
		Write(x, y, o[0], o[1], o[2], tag = tag)
		x = x + len(o[0])

gHasSetSize = False
def WndProc(hwnd, message, wParam, lParam):
	global gConf, gCoData
	fontWidth = gConf['fontWidth']
	fontHeight = gConf['fontHeight']
	colCnt = gConf['colCnt']
	rowCnt = gConf['rowCnt']
	tickCb = gConf['tickCb']
	keyCb = gConf['keyCb']
	clickCb = gConf['clickCb']

	ps = PAINTSTRUCT()
	rect = RECT()
	if message == win32con.WM_TIMER:
		tickCb()
		windll.user32.GetClientRect(c_int(hwnd), byref(rect))
		windll.user32.InvalidateRect(c_int(hwnd), byref(rect), 0)
		return 0
	if message == win32con.WM_LBUTTONUP:
		x = lParam & 0x0ffff
		y = lParam >> 16
		x = int(x / fontWidth)
		y = int(y / fontHeight)
		tag = gCoData[y * colCnt + x][3]
		if tag != None:
			clickCb(tag)
		return 0
	if message == win32con.WM_CHAR:
		keyCb(wParam)
		return 0
	if message == win32con.WM_PAINT:
		'''

		'''
		hfont = gConf['hfont']
		if hfont is None:
			return 0


		hdc = windll.user32.BeginPaint(c_int(hwnd), byref(ps))
		windll.gdi32.SelectObject(hdc, hfont)
		windll.gdi32.SetBkMode(c_void_p(hdc), win32con.OPAQUE)
		y = 0
		while y < rowCnt:
			row = []
			color = (-1, -1)
			x = 0
			'''
				Slow/Simple/Light/Ugly

				* used for debugging.. if complex routine is screwing up this will show it..
			'''
			while x < colCnt:
				v = gCoData[y * colCnt + x]
				c = v[0]
				fg = v[1]
				bg = v[2]
				windll.gdi32.SetBkColor(c_void_p(hdc), c_int(bg))
				windll.gdi32.SetTextColor(c_void_p(hdc), c_int(fg))
				windll.gdi32.TextOutA(c_void_p(hdc), c_int(x * fontWidth), c_int(fontHeight * y), bytes(c, 'utf8'), 1)	
				x = x + 1
			'''
				Fast/Complex/Heavy/Pretty

				* supports anti-aliasing effect because draws strings not characters.
			'''
			'''
			x = 0
			s = 0
			while x < colCnt:
				v = gCoData[y * colCnt + x]
				c = v[0]
				fg = v[1]
				bg = v[2]
				if (color[0] != fg or color[1] != bg) and (len(row) > 0):
					windll.gdi32.SetBkColor(c_int(hdc), c_int(color[1]))
					windll.gdi32.SetTextColor(c_int(hdc), c_int(color[0]))
					windll.gdi32.TextOutA(c_int(hdc), c_int(s * fontWidth), c_int(fontHeight * y), bytes(''.join(row), 'utf8'), len(row))
					s = x
					row = []
				color = (fg, bg)
				row.append(c)
				x = x + 1
			if len(row) > 0:
				windll.gdi32.SetBkColor(c_int(hdc), c_int(color[1]))
				windll.gdi32.SetTextColor(c_int(hdc), c_int(color[0]))
				windll.gdi32.TextOutA(c_int(hdc), c_int(s * fontWidth), c_int(fontHeight * y), bytes(''.join(row), 'utf8'), len(row))
			'''
			y = y + 1
		windll.user32.EndPaint(c_int(hwnd), byref(ps))
		#windll.gdi32.DeleteObject(hfont)
		return 0
	elif message == win32con.WM_DESTROY:
		windll.user32.PostQuitMessage(0)
		return 0

	DefWndProc = windll.user32.DefWindowProcA
	DefWndProc.argtypes = [c_int, c_int, c_int, c_int]
	r = DefWndProc(c_int(hwnd), c_int(message), c_int(wParam), c_int(lParam))
	return r

if __name__=='__main__':
	sys.exit(MainWin(10, 0, 120, 40), None, None)
