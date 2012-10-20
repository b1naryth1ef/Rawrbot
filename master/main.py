import redis, json, thread, random
import sys, os, time
from collections import deque
from parser import Parser
from data import ConfigFile
import api

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
chunks = lambda l, n: [l[x: x+n] for x in xrange(0, len(l), n)]

red = redis.Redis(host="hydr0.com", password="")
cfg = ConfigFile(name="config", default=default_cfg)
api.A = api.API(red)

class Worker(object):
    def __init__(self, id, net):
        self.id = id
        self.nick = net.nickkey+'-%s' % self.id
        self.nid = net.id
        self.net = net
        self.chans = []
        self.ready = False
        self.waitPing = False

    def push(self, tag, **k):
        k['tag'] = tag
        red.rpush('i.%s.worker.%s' % (self.nid, self.id), json.dumps(k))

    def setup(self, reply):
        red.publish(reply, json.dumps({
                'id':self.id,
                'nid':self.nid,
                'server':self.net.name,
                'auth':self.net.auth,
                'nick':self.nick
            }))
        thread.start_new_thread(self.getReady, ())

    def join(self, chan, send=True):
        self.chans.append(chan)
        self.net.channels[chan] = self
        if send: self.push('JOIN', chan=chan)

    def part(self, chan, msg, send=True):
        self.chans.remove(chan)
        self.net.channels[chan] = None
        if send: self.push('PART', chan=chan, msg=msg)

    def ping(self):
        if not self.ready: return
        self.waitPing = True
        self.push('PING')
        time.sleep(15)
        if self.waitPing:
            self.quit('Timed out!')

    def quit(self, msg="!!"):
        print 'Worker #%s is quitting... %s' % (self.id, msg)
        for i in self.chans:
            self.net.channels[i] = None
        self.push('SHUTDOWN', msg=msg)
        self.net.rmvWorker(self.id)

    def getReady(self):
        time.sleep(20)
        if not self.ready:
            print 'Worker going down for not getting ready in time!'
            self.quit()

    def parse(self, msg):
        if msg['tag'] == 'READY': 
            self.ready = True
            self.net.setupWorker(self.id)
        elif msg['tag'] == 'PONG': 
            self.waitPing = False
        elif msg['tag'] == 'BYE':
            self.quit("Shutdown on worker side")
        else:
            print msg

class Network(object):
    def __init__(self, id, name, master, channels=[], auth=""):
        self.id = id
        self.name = name
        self.master = master
        self.channels = dict([(i.replace('#', ''), None) for i in channels])
        self.auth = auth
        self.nickkey = "RawrBot"
        self.workers = {}

    def boot(self):
        red.delete('i.%s.chans' % self.id)
        red.delete('i.%s.workers' % self.id)
        for chan in self.channels.keys():
            red.delete('i.%s.chan.%s.users' % (self.id, chan))
        red.set('i.%s.nickkey' % self.id, self.nickkey)
        red.sadd('i.%s.chans' % self.id, *self.channels)

    def quit(self, msg):
        for i in self.workers.values():
            if i != None: i.quit(msg)

    def write(self, chan, msg):
        if chan in self.channels.keys():
            k = {'tag':'MSG', 'msg':msg}
            red.rpush('i.%s.chan.%s' % (self.id, self.chan), json.dumps(k))

    def joinChannel(self, chan):
        chan = chan.replace('#', '')
        red.delete('i.%s.chan.%s' % (self.id, chan))
        m = None
        for i in self.workers.values():
            if m == None: m = i
            elif len(m.chans) > len(i.chans): m = i
        self.channels[chan] = m
        if m != None:
            m.join(chan)
            red.sadd('i.%s.chans' % self.id, chan)

    def partChannel(self, chan, msg="Leaving..."):
        chan = chan.replace('#', '')
        red.delete('i.%s.chan.%s' % (self.id, chan))
        self.channels[chan].part(chan, msg)
        red.srem('i.%s.chans' % self.id, chan)
        self.channels[chan] = None

    def getNumWorkers(self):
        return red.get('i.%s.workers' % self.id)

    def addWorker(self, reply):
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

        red.sadd('i.%s.workers' % self.id, k)
        red.delete('i.%s.worker.%s' % (self.id, k)) #Make sure we empty stuff
        self.workers[k].setup(reply)

    def setupWorker(self, k):
        q = lambda: [i for i in self.workers.values() if i != None]
        if len(self.workers) <= 1:
            for chan in self.channels.keys():
                self.workers[k].join(chan)
        else:
            if len(self.channels) > len(q()):
                limit = len(self.channels) - len(q())
            else:
                limit = len(self.channels)
            c = chunks(self.channels.keys(), limit)
            print c
            for pos, w in enumerate(self.workers.values()):
                if w == None: continue
                if pos+1 > len(c): break
                for i in c[pos]:
                    if i in w.chans: continue
                    self.channels[i].part(i, 'Bot Swapping...')
                    w.join(i)

    def rmvWorker(self, wid): #@TODO Reallocate channels?
        red.srem('i.%s.workers' % self.id, wid)
        self.workers[wid] = None

    def ping(self):
        for i in self.workers.values():
            if i == None: continue
            thread.start_new_thread(i.ping, ())

    def recover(self, m):
        print 'Recovering worker #%s' % m['id']
        m['id'] = int(m['id'])
        self.workers[m['id']] = Worker(m['id'], self)
        for i in m['chans']:
            self.workers[m['id']].join(i.replace('#', ''), send=False)

class Master(object):
    def boot(self):
        self.parent, self.id = self.getID()
        self.active = True
        self.isMaster = False if self.parent else True
        self.networks = {}
        self.sub = red.pubsub()
        self.netchoice = 1
        self.update()
        self.parser = Parser(red, api.A)

        for num, i in enumerate(cfg.networks):
            self.networks[num] = Network(num, i['host'], self, channels=i['chans'], auth=i['auth'])

        thread.start_new_thread(self.readLoop, ())
        thread.start_new_thread(self.pingLoop, ())
        thread.start_new_thread(self.parser.parseLoop, ()) #@DEV Just while we dont use start.py

        try:
            if self.isMaster:
                red.delete('i.parseq')
                for i in self.networks.values():
                    i.boot()
                thread.start_new_thread(self.masterLoop, ())
            while True:
                time.sleep(5) #Keep threads running
        except: 
            if red.zcard('i.masters') > 1: red.publish('irc.m', json.dumps({'tag':'MOVE'}))
            else:
                for i in self.networks.values():
                    if i != None: i.quit("MAYDAY! We're going down!")
                sys.exit()
        finally:
            red.zrem('i.masters', self.id)
    
    def update(self):
        red.zadd('i.masters', self.id, self.id)
        
    def getID(self):
        q = red.zcard('i.masters')
        if q != 0:
            return q, q+1
        return None, 1
        
    def push(self, c, tag, **kwargs):
        kwargs['tag'] = tag.upper()
        red.lpush(c, json.dumps(kwargs))

    def recover(self):
        self.isMaster = True
        self.parent = None
        thread.start_new_thread(self.masterLoop, ())
        for nid in self.networks.keys():
            for i in red.smembers('i.%s.workers' % nid):
                red.rpush('i.%s.worker.%s' % (nid, i), json.dumps({'tag':'ID'}))

    def readLoop(self):
        self.subby = red.pubsub()
        self.subby.subscribe('irc.m.%s' % self.id)
        self.subby.subscribe('irc.m')
        while self.active:
            for q in self.subby.listen():
                try: q = json.loads(q['data'])
                except: 
                    print '>>>', q
                    continue
                if q['tag'] == 'PING': red.lpush('i.temp.%s' % q['chan'], 'PONG')
                elif q['tag'] == 'MOVE':
                    print 'Moving!'
                    self.id -= 1
                    self.parent -= 1
                    self.update()
                    if self.id == 1: self.recover()
        self.subby.unsubscribe('irc.m.%s' % self.id)
        self.subby.unsubscribe('irc.m')

    def masterLoop(self):
        self.sub.subscribe('irc.master')
        while self.active:
            for msg in self.sub.listen():
                try: msg = json.loads(msg['data'])
                except: 
                    print '>>>', msg
                    continue
                if msg['tag'] == 'HI': thread.start_new_thread(self.addWorker, (msg['resp'],)) #@NOTE This is threaded so we can sleep
                elif msg['tag'] == 'ID': 
                    self.networks[msg['nid']].recover(msg)
                elif 'nid' in msg and 'id' in msg:
                    if self.networks[msg['nid']].workers[msg['id']] != None:
                        self.networks[msg['nid']].workers[msg['id']].parse(msg)
        self.sub.unsubscribe('irc.master')

    def pingLoop(self):
        print 'Is Master: %s' % self.isMaster
        while self.active:
            if self.isMaster:
                for i in self.networks.values():
                    i.ping()
            else:
                c = rand()
                red.publish('irc.m.%s' % self.parent, json.dumps({'tag':'PING', 'chan':c}))
                if not red.blpop('i.temp.%s' % c, 10):
                    print 'Master #%s timed out on ping! Moving up in the line...' % self.parent
                    red.delete('i.masters')
                    red.publish('irc.m', json.dumps({'tag':'MOVE'}))
            time.sleep(20)

    def addWorker(self, reply):
        print 'Adding worker!'
        m = None
        for i in self.networks.values():
            if m == None: m = i
            elif m.getNumWorkers() > i.getNumWorkers(): m = i
        if m != None:
            while len([i for i in m.workers.values() if i != None and i.ready == False]):
                time.sleep(1)
            m.addWorker(reply)

#@TODO Add parsing of BYE tag

m = Master()
m.boot()