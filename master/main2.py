import redis, json, thread, random
import sys, os, time
from collections import deque
from parser import Parser
from data import ConfigFile

default_cfg = {
	'networks':[
		{
			'host':'irc.esper.net',
			'chans':['b0tt3st', 'testy1', 'testy2', 'testy3', 'b1naryth1ef'],
			'auth':'',
		}
	],
	'plugins':['util']
}

rand = lambda: random.randint(11111, 99999)

red = redis.Redis(host="hydr0.com", password="")
cfg = ConfigFile(name="config", default=default_cfg)

class Worker(object):
	def __init__(self, id, net):
		self.id = id
		self.nick = net.nickkey % self.id
		self.nid = net.id
		self.net = net
		self.chans = []
		self.ready = False

	def push(self, tag, **k):
		k['tag'] = tag
		red.publish('irc.%s.w.%s' % (self.nid, self.id), json.dumps(k))

	def setup(self, reply):
		red.publish(reply, json.dumps({
				'id':self.id,
				'nid':self.nid,
				'server':self.net.name,
				'auth':self.net.auth,
				'nick':self.nick
			}))

	def join(self, chan):
		self.chans.append(chan)
		self.push('JOIN', chan=chan)

	def part(self, chan, msg):
		self.chans.remove(chan)
		self.push('PART', chan=chan, msg=msg)

	def ping(self): pass

	def quit(self, msg="!!"):
		self.push('SHUTDOWN', msg=msg)

	def getReady(self):
		time.sleep(20)
		if not self.ready:
			print 'Worker going down for not getting ready in time!'
			self.quit()

	def parse(self, msg):
		if msg['tag'] == 'READY':
			self.ready = True

class Network(object):
	def __init__(self, id, name, master, channels=[], auth=""):
		self.id = id
		self.name = name
		self.master = master
		self.channels = dict([(i.replace('#', ''), None) for i in channels])
		self.auth = auth
		self.nickkey = "RawrBot-%s"
		self.workers = {}

		red.set('i.n.%s.workers' % self.id, 0)
		for i in self.channels:
			red.set('i.n.%s.c.%s' % (self.id, i), 0)

	def joinChannel(self, chan):
		chan = chan.replace('#', '')
		m = None
		for i in self.workers.values():
			if m == None: m = i
			elif len(m.chans) > len(i.chans): m = i
		self.channels[chan] = m
		if m != None:
			m.join(chan)

	def partChannel(self, chan, msg="Leaving..."):
		chan = chan.replace('#', '')
		self.channels[chan].part(chan, msg)
		del self.channels[chan]

	def getNumWorkers(self):
		return red.get('i.n.%s.workers' % self.id)

	def addWorker(self, reply):
		red.incr('i.n.%s.workers' % self.id)
		if None in self.workers.values():
			for k in self.workers:
				if self.workers[k] == None:
					self.workers[k] = Worker(k, self)
					break
		elif len(self.workers):
			k = max(self.workers.keys())+1
			self.workers[k] = Worker(k, self)
		else:
			k = 1
			self.workers[k] = Worker(k, self)

		num = len(self.channels)/len(self.workers)
		c = self.channels.keys()
		random.shuffle(c)
		for i in c:
			if num <= 0: break
			if self.channels[i] != None:
				self.channels[i].part(i, msg='Bot Swapping!')
			self.workers[k].join(i)
			num -= 1
		self.workers[k].setup(reply)

	def rmvWorker(self, wid):
		red.incr('i.n.%s.workers' % self.id, -1)
		self.workers[wid].quit()
		del self.workers[wid]

	def ping(self):
		for i in self.workers.values():
			i.ping()

class Master(object):
	def boot(self):
		self.parent, self.id = self.getID()
		self.active = True
		self.isMaster = False if self.parent else True
		self.networks = {}
		self.sub = red.pubsub()
		self.netchoice = 1
		self.update()

		for num, i in enumerate(cfg.networks):
			self.networks[num] = Network(num, i['host'], self, channels=i['chans'], auth=i['auth'])

		thread.start_new_thread(self.readLoop, ())
		thread.start_new_thread(self.pingLoop, ())

		try:
			if self.isMaster:
				thread.start_new_thread(self.masterLoop, ())
			while True:
				time.sleep(5) #Keep threads running
		except KeyboardInterrupt:
			red.zrem('i.masters', self.id)
	
	def update(self):
		print self.id, self.parent
		red.zadd('i.masters', self.id, self.id)
		
	def getID(self):
		q = red.zrangebyscore('i.masters', 0, 999, withscores=True)
		print q
		if len(q):
			return int(q[-1][0]), int(q[-1][1])+1
		return None, 1
		
	def push(self, c, tag, **kwargs):
		kwargs['tag'] = tag.upper()
		red.lpush(c, json.dumps(kwargs))

	def readLoop(self):
		while self.active:
			time.sleep(1)
			q = red.lpop('irc.m.%s' % self.id)
			if q:
				try: q = json.loads(q)
				except: 
					print '>>>', q
					continue
				if q['tag'] == 'PING': red.lpush('i.temp.%s' % q['chan'], 'PONG')
				elif q['tag'] == 'MOVE':
					self.id -= 1
					self.parent -= 1
		
	def masterLoop(self):
		self.sub.subscribe('irc.master')
		while self.active:
			for msg in self.sub.listen():
				try: msg = json.loads(msg['data'])
				except: 
					print '>>>', msg
					continue
				if msg['tag'] == 'HI': self.addWorker(msg['resp'])
				elif 'nid' in msg and 'id' in msg:
					self.networks[msg['nid']].workers[msg['id']].parse(msg) #@TODO Fix this shit
		self.sub.unsubscribe('irc.master')

	def pingLoop(self):
		while self.active:
			if self.isMaster:
				for i in self.networks.values():
					i.ping()
			else:
				c = rand()
				self.push('irc.m.%s' % self.parent, 'PING', chan=c)
				if not red.blpop('i.temp.%s' % c, 10):
					print 'Master #%s timed out on ping! Moving up in the line...' % self.parent
					q = red.zrange('i.masters', self.id, -1)
					red.zrem('i.masters', self.parent)
					if len(q): #@TODO Make sure we remove any tags in i.masters
						self.push('irc.m.%s' % q[0], 'MOVE')
						self.id -= 1
						self.update()
					if self.id == 1: 
						self.isMaster = True
						self.parent = None
						thread.start_new_thread(self.masterLoop, ())
			time.sleep(30)

	def addWorker(self, reply):
		print 'Adding worker!'
		m = None
		for i in self.networks.values():
			if m == None: m = i
			elif m.getNumWorkers() > i.getNumWorkers(): m = i
		if m != None: m.addWorker(reply)

m = Master()
m.boot()