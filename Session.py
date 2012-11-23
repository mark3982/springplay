import os
import sys
import socket
import hashlib
import base64
import asyncore
import traceback

LOG_PACKET = 200
LOG_HEAVY = 100
LOG_LIGHT = 50

#LOG_HEAVY = 200

def loghdlr(session, level, msg):
	if session['loglvl'] >= level:
		if session['loghdlr'] is not None:
			session['loghdlr'](session, level, msg)
			return
		print('log: %s' % (msg))
	return

def TASPasswordHash(passw):
	md5 = hashlib.md5()
	md5.update(passw)
	hash = md5.digest()
	hash = base64.b64encode(hash)
	return hash

def Create(nick, passw, server = 'lobby.springrts.com', port = 8200, loghdlr = None, loglvl = LOG_HEAVY):
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.connect((server, port))
	sock.setblocking(0)
	session = {	'socket': sock, 
			'nick': nick, 
			'passw': passw, 
			'buf': None, 
			'got-server-welcome': False,
			'loghdlr': loghdlr,
			'loglvl': loglvl,
			'throwbk': [],
			'channels': {},
	}
	return session

def wrapCb(cb, session, event, args):
	try:
		cb(session, event, args)
	except Exception as e:
		traceback.print_exc()
	
def Update(session, cb):
	sock = session['socket']
	try:
		data = sock.recv(4096 * 4)
	except Exception as E:
		return
	loghdlr(session, LOG_PACKET, '---network-lobby-data---')
	loghdlr(session, LOG_PACKET, '%s' % (data))
	segs = []
	buf = session['buf']
	off = 0
	loghdlr(session, LOG_PACKET, '---enter-message-spliter---')
	while True:
		pos = data.find(b'\n', off)
		if pos < 0:
			if len(data) > off:
				session['buf'] = data[off:]
				loghdlr(session, LOG_PACKET, '--hold|buf|wait:%s' % data[off:])
			break
		if buf is not None: 
			seg = buf + data[off:pos]
			buf = None
			session['buf'] = None
		else:
			seg = data[off:pos]
		off = pos + 1
		segs.append(bytes.decode(seg, 'utf8'))
		loghdlr(session, LOG_PACKET, '--seg|msg|cmd:%s' % seg)
	loghdlr(session, LOG_PACKET, '---exit-message-spliter---')

	if session['got-server-welcome'] is False:
		session['got-server-welcome'] = True
		session['server-string'] = segs.pop(0)
		loghdlr(session, LOG_LIGHT, 'server-string[%s]' % (session['server-string']))
		clientid = 'springplay 000-000-000-a (leonard kevin mcguire jr)'
		localip = socket.gethostbyname(socket.gethostname())
		passwhash = bytes.decode(TASPasswordHash(bytes(session['passw'], 'utf8')), 'utf8')
		localip = '192.168.1.5'
		loginstr = 'LOGIN %s %s %s %s %s\n' % (session['nick'], passwhash, '2194', localip, clientid)
		session['socket'].send(bytes(loginstr, 'utf8'))
		session['users'] = {}
		session['battles'] = {}

	# handles situations where server sends something out of order, so we throw it back
	# until we can handle it correctly, keeps from having to place code in functions or
	# duplicate it thus creating situation for bugs.. here we just have a big detectable
	# memory leak..
	#print('throwbk', len(session['throwbk']))
	for seg in session['throwbk']:
		segs.append(seg)
	session['throwbk'] = []
	
	# actually process messages
	for seg in segs:
		parts = seg.split(' ')
		#print(parts[0])
		if parts[0] == 'ADDUSER':
			#loghdlr(session, LOG_HEAVY, 'adduser %s %s %s' % (parts[1], parts[2], parts[3]))
			wrapCb(cb, session, 'adduser', {
				'user':			parts[1],
				'country':		parts[2],
				'id':			parts[3]
			})
			continue
		if parts[0] == 'CLIENTS':
			b_channel = parts[1]
			wrapCb(cb, session, 'clients', {
				'channel':		b_channel,
				'unknown':		parts[2:]
			})
			continue
		if parts[0] == 'JOIN':
			wrapCb(cb, session, 'join', {
				'unknown':		parts[1]
			})
			continue
		if parts[0] == 'JOINED':
			b_channel = parts[1]
			b_nick = parts[2]
			wrapCb(cb, session, 'joined', {
				'channel':		b_channel,
				'user':			b_nick
			})
			continue
		if parts[0] == 'LEFT':
			b_channel = parts[1]
			b_nick = parts[2]
			b_msg = ' '.join(parts[3:])
			wrapCb(cb, session, 'left', {
				'channel':		b_channel,
				'user':			b_nick,
				'message':		b_msg
			})
			continue
		if parts[0] == 'SAID':
			b_channel = parts[1]
			b_nick = parts[2]
			b_msg = seg[4 + len(parts[1]) + 1 + len(parts[2]) + 1:]
			wrapCb(cb, session, 'said', {
				'channel':		b_channel,
				'user':			b_nick,
				'message':		b_msg
			})
			continue
		if parts[0] == 'ACCEPTED':
			loghdlr(session, LOG_LIGHT, 'lobby accepted our connection')
			wrapCb(cb, session, 'accepted', None)
			continue
		if parts[0] == 'DENIED':
			loghdlr(session, LOG_PACKET, 'lobby denied our connection (%s)' % seg[7:])
			wrapCb(cb, session, 'denied', {'reason': seg[7:]})
			continue
		if parts[0] == 'MOTD':
			loghdlr(session, LOG_PACKET, 'lobby-motd %s' % seg[5:])
			wrapCb(cb, session, 'motd', {'motd': seg[5:]})
			continue
		if parts[0] == 'BATTLEOPENED':
			b_id = parts[1]
			b_type = parts[2]
			b_nat = parts[3]
			b_user = parts[4]
			b_host = parts[5]
			b_port = int(parts[6])
			b_maxplayers = int(parts[7])
			b_haspass = parts[8]
			b_rank = parts[9]
			b_hash = parts[10]
			
			eparts = ' '.join(parts[11:])
			eparts = eparts.split('\t')
			b_map = eparts[0]
			b_desc = eparts[1]
			b_mod = eparts[2]
			
			wrapCb(cb, session, 'battleopened', {
					'user':			b_user,
					'type':			b_type,
					'nat':			b_nat,
					'maxPlayers':	b_maxplayers,
					'id':			b_id,
					'host':			b_host,
					'port':			b_port,
					'hash':			b_hash,
					'rank':			b_rank,
					'hasPass':		b_haspass,
					'map':			b_map,
					'desc':			b_desc,
					'mod':			b_mod
				}
			)
			continue
		if parts[0] == 'BATTLECLOSED':
			# need to change
			b_id = parts[1]
			wrapCb(cb, session, 'battleclosed', {
				'id':				b_id,
			})
			continue
		if parts[0] == 'UPDATEBATTLEINFO':
			b_id = parts[1]
			b_specs = int(parts[2])
			b_hasPass = parts[3]
			b_hash = parts[4]
			b_map = ' '.join(parts[5:])
			wrapCb(cb, session, 'updatebattleinfo', {
				'id':				b_id,
				'specs':			b_specs,
				'map':				b_map,
				'hasPass':			b_hasPass,
				'hash':				b_hash
			})
			continue
		if parts[0] == 'JOINEDBATTLE':
			b_id = parts[1]
			b_nick = parts[2]
			wrapCb(cb, session, 'joinedbattle', {
				'user':			b_nick,
				'id':			b_id
			})
			continue
		if parts[0] == 'CLIENTSTATUS':
			b_nick = parts[1]
			b_status = int(parts[2])
			
			bot = (b_status >> 6) & 1 == 1
			moderator = (b_status >> 5) & 1 == 1
			rank = (b_status >> 2) & 7 
			away = (b_status >> 1) & 1 == 1
			ingame = b_status & 1 == 1
			
			wrapCb(cb, session, 'clientstatus', {
				'user':			b_nick,
				'isBot':		bot,
				'inGame':		ingame,
				'isAway':		away,
				'rank':			rank,
				'isMod':		moderator
			})
			continue
		if parts[0] == 'LOGININFOEND':
			#JoinChannel(session, 'en')
			continue
		if parts[0] == 'LEFTBATTLE':
			b_id = parts[1]
			b_nick = parts[2]
			wrapCb(cb, session, 'leftbattle', {
				'user':		b_nick,
				'id':		b_id
			})
			continue
		if parts[0] == 'REMOVEUSER':
			b_nick = parts[1]
			wrapCb(cb, session, 'removeuser', {'user': b_nick})
			continue
		if parts[0] == 'CHANNELTOPIC':
			channel = parts[1]
			whom = parts[2]
			flags = int(parts[3])
			offset = len(parts[0]) + 1 + len(parts[1]) + 1 + len(parts[2]) + 1 + len(parts[3]) + 1
			message = seg[offset:]
			wrapCb(cb, session, 'channeltopic', {
				'channel':		channel,
				'user':			whom,
				'flags':		flags,
				'message':		message
			})
			continue 
		if parts[0] == 'SAIDBATTLE':
			whom = parts[1]
			message = seg[len(parts[0]) + 1 + len(parts[1]) + 1:]
			wrapCb(cb, session, 'saidbattle', {
				'user':			whom,
				'message':		message
			})
			continue
			
		print('------UNKNOWN NETWORK MESSAGE------')
		print(parts)
		exit()
	return

'''
	Helper Type Functions

	One just taps into our routines that automatically
	track who is in the channel (joins/leaves). The other
	keeps track of open battles and information about 
	them. But, all could have been implemented externally.
'''
def GetChannelInfo(session, channel):
	if channel not in session['channels']:
		return None
	return session['channels'][channel]
def GetBattleInfo(session, battleid):
	if battleid not in session['battles']:
		return None
	return session['battles'][battleid]
def GetUsers(session):
	return session['users']
def GetChannels(session):
	return session['channels']
def GetBattles(session):
	return session['battles']
def LeaveChannel(session, channel):
	session['socket'].send(bytes('LEAVE %s\n' % (channel), 'utf8'))
	cb(session, 'leave', (channel,))
def JoinChannel(session, channel):
	session['socket'].send(bytes('JOIN %s\n' % (channel), 'utf8'))
def JoinBattle(session, id, passw):
	session['socket'].send(bytes('JOINBATTLE %s %s\n' % (id, passw), 'utf8'))
def ChannelSay(session, channel, msg):
	session['socket'].send(bytes('', 'utf8'))

'''
	LEAVE <channel>
	JOIN <channel>
	CLIENTS <clients>
	JOINBATTLE <id> <passw-hash>
	
'''

def tcb(session, reason, args):
	return

#session = sessionCreate('kmcguire', 'tty5413413')
#while True:
#	sessionUpdate(session, tcb)