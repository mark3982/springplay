import os
import hashlib
'''
	The automatic version tracker. It keeps track of changes on different modules and
	updates our version string correctly.

	<total-developmental-runs>-<modules-in-build>-<version-of-each-module>

	First, load version data, compute stuff, save version data.
	Next, compute version string.
'''
if os.path.exists('version'):
	fd = open('version', 'r')
	data = fd.read()
	fd.close()
	tmp = eval(data)
	modules = tmp[0]
	tdr = tmp[1]
else:
	tdr = 0
	modules = {}

nodes = os.listdir('./')

fmods = {}
for node in nodes:
	if node[-3:] == '.py':
		fd = open(node, 'rb')
		data = fd.read()
		fd.close()
		sha512 = hashlib.sha512()
		sha512.update(data)
		hash = sha512.digest()
		fmods[node] = hash

'''
	Format of:
		(<unique-id>, <module-hash>, <module-change-incrementor>)
'''
for fmod in fmods:
	if fmod in modules:
		if fmods[fmod] != modules[fmod][1]:
			modules[fmod] = (modules[fmod][0], fmods[fmod], modules[fmod][2] + 1)
	else:
		modules[fmod] = (len(modules), fmods[fmod], 0)

tdr = tdr + 1
fd = open('version', 'w')
fd.write('%s' % ([modules, tdr]))
fd.close()

vstr = []
for k in modules:
	mod = modules[k]
	uid = mod[0]
	if uid > 25:
		uid = chr(ord('A') + (uid - 26))
	else:
		uid = chr(ord('a') + uid)
	chgid = mod[2] & 0x0ff
	vstr.append('%s%d' % (uid, chgid))

ver_id = ''.join(vstr)
ver_tdr = tdr

def getVersionString():
	global ver_id
	global ver_tdr
	return '%s.%s' % (ver_tdr, ver_id)