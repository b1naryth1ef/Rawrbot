import redis, json, thread
from collections import OrderedDict, deque
from api import A
from data import ConfigFile
import sys, os, time, random

default_cfg = {
  'servers':
    [
      {
        'host':'irc.quakenet.org',
        'chans':['b0tt3st', 'Testy1', 'B1naryTh1ef'],
        'auth':''
      }
    ],
  'admins':['b1naryth1ef']
}

red = redis.Redis(host="hydr0.com", password="")
cfg = ConfigFile(name="main", default=default_cfg)
plugins = ['web', 'util']

class Channel(object): #ASSUME WE HAVE #
    def __init__(self, network, name, topic=""):
        self.network = network
        self.name = name.replace('#', '')
        self.topic = topic
        self.users = {}

    def setTopic(self, topic): #@TODO Fire event
        self.topic = topic

    def addByNames(self, names):
        for i in names:
            if i in self.users: return
            op, voice = False, False
            if i.startswith('@'): op = True
            if i.startswith('+'): voice = True
            self.users[i] = {'op':op, 'voice':voice}

    def addByNick(self, nick):
        if nick in self.users: return #@TODO Eventually throw an error or warning here
        self.users[nick] = {'op':False, 'voice':False}

    def rmvByNick(self, nick):
        if nick in self.users:
            del self.users[nick]

    def write(self, chan, msg=""):
        self.network.write(self.name, msg)

class Network(object):
    def __init__(self, id, name, master, channels=[], auth=""):
        self.id = id
        self.name = name
        self.master = master
        self.nickbase = "RawrBot-"
        self.auth = auth

        self.channels = OrderedDict([(i.lower(), Channel(self, i.lower())) for i in channels]) #NAME :> CHANNEL
        self.users = {}
        self.workers = {}
        self.writes = dict([(i, deque()) for i in self.channels.keys()])

    def writeGlobal(self, msg):
        for chan in self.channels.keys():
            self.write(chan, msg)

    def hasChan(self, chan):
        if chan.startswith('#'): chan = chan[1:]
        if chan in self.channels.keys():
            return True
        return False

    def getWorker(self):
        #@DEV What ID are we?
        def _getid():
            if len(self.workers):
                if None in self.workers.values():
                    for i in self.workers:
                        if self.workers[i] == None:
                            return i
                else: return max(self.workers.keys())+1
            else: return 1

        w = Worker(_getid(), self, auth=self.auth)
        return w

    def write(self, chan, msg=""):
        if chan.startswith('#'): chan = chan[1:]
        w = self.writes[chan.lower()].popleft()
        w.push("MSG", chan=chan, msg=msg)
        self.writes[chan.lower()].append(w)
        print '%s -> %s' % (msg, chan)

    def addWorker(self, worker):
        self.workers[worker.id] = worker
        #self.workers[worker.id].getChannels() #@DEV This is done when we're ready

    def rmvWorker(self, wid):
        self.workers[wid] = None

    def quit(self):
        for i in self.workers.values():
            if not i: continue
            i.push('SHUTDOWN')

    def ping(self):
        for worker in self.workers.values():
            if worker: worker.ping()
        time.sleep(15)
        for worker in self.workers.values():
            if not worker: continue
            if worker.waitingForPong:
                print "Worker #%s timed out on pong!" % worker.id
                worker.kill()

class Worker(object):
    def __init__(self, wid, network, auth=""):
        self.id = wid
        self.network = network
        self.auth = auth
        self.A = self.network.master.A
        self.channels = []
        self.idles = []
        self.whois = {}

        self.ready = False
        self.active = True
        self.waitingForPong = False

    def getUserInfo(self, user): #@TODO If we call this at the same time, one function wont get the call back D:
        chan = str(random.randint(1111, 9999))
        self.push('UINFO', user=user, chan=chan)
        val = red.blpop(chan, 15)
        try:
            val = json.loads(val[1])
        except:
            print "Cannot load getUserInfo!"
            return None
        return val

    def setup(self, chan):
        self.nick = "%s%s" % (self.network.nickbase, self.id)
        self.chan = "irc.worker.%s" % self.id
        self.network.addWorker(self)
        red.publish(chan, json.dumps({
            'id':self.id,
            'nick':self.nick,
            'server':self.network.name,
            'nid':self.network.id,
            'auth':self.auth
        }))
        thread.start_new_thread(self.waitForReady, ())

    def getChan(self, name):
        return self.network.channels[name.strip()]

    def parse(self, m):
        if 'chan' in m.keys():
            m['chan'] = m['chan'].replace('#', '').lower()
        if m['tag'] == "BYE": 
            self.kill()
        elif m['tag'] == "MSG":
            print 'MSG: %s >> %s | %s' % (m['nick'], m['dest'], m['msg'])
            if m['nick'].startswith(self.network.nickbase): return
            if self.A.parse(self, m): return
            if m['dest'].startswith('#'):
                self.A.fireHook('chanmsg', chan=m['dest'].replace('#', ''), nick=m['nick'], msg=m['msg'], m=m['msg'].split(' '), w=self)
            else:
                self.A.fireHook('privmsg', nick=m['nick'], msg=m['msg'], m=m['msg'].split(' '), w=self)
        elif m['tag'] == "NAMES": self.getChan(m['chan']).addByNames(m['nicks'])
        elif m['tag'] == "TOPIC": self.getChan(m['chan']).setTopic(m['topic'])
        elif m['tag'] == "JOIN":
            self.A.fireHook('join', nick=m['nick'], chan=m['chan'], w=self)
            self.getChan(m['chan']).addByNick(m['nick'])
        elif m['tag'] == "PART":
            self.A.fireHook('part', nick=m['nick'], chan=m['chan'], msg=m['msg'], w=self)
            self.getChan(m['chan']).rmvByNick(m['nick'])
        elif m['tag'] == "READY":
            self.ready = True
            self.getChannels()
        elif m['tag'] == "PONG": self.waitingForPong = False
        else: print m

    def getChannels(self): #@TODO Implement more bots per channel
        num = (len(self.network.channels)/len(self.network.workers))
        num2 = num

        if len(self.network.workers) > 1:
            while num >= -num2:
                for i in self.network.workers.values():
                    if i != self:
                        if num > 0:
                            c = i.channels[0]
                            i.partChannel(c)
                            self.joinChannel(c)
                            num -= 1
                        elif num >= -num2:
                            c = i.channels[0]
                            self.joinChannel(c, idle=True)
                            num -=1

        else:
            for i in self.network.channels.values():
                self.joinChannel(i)

    def write(self, chan, msg):    
        self.network.write(chan, msg)

    def writeUser(self, user, msg): #@NOTE This should /never/ be random, or pms will be in different tabs for users.
        self.push('UMSG', user=user, msg=msg)

    def push(self, tag, **kwargs):
        kwargs['tag'] = tag
        red.publish(self.chan, json.dumps(kwargs)) #@DEV If we want, we can eventually zlib this

    def kill(self):
        print 'Worker #%s is going down.' % self.id
        self.network.rmvWorker(self.id)
        self.active = False

    def joinChannel(self, chan, idle=False):
        if isinstance(chan, Channel):
            chan = chan.name       
        if idle:  self.idles.append(chan)
        else: self.channels.append(chan)
        self.network.writes[chan].append(self)
        self.push("JOIN", chan="#"+chan, idle=idle)

    def partChannel(self, chan, msg="Bot Swap...", idle=False):
        if isinstance(chan, Channel):
            chan = chan.name
        if idle:
            self.idles.pop(self.idles.index(chan))
        else:
            self.channels.pop(self.channels.index(chan))
        self.network.writes[chan].remove(self)
        self.push("PART", chan="#"+chan, msg=msg)

    def waitForReady(self):
        time.sleep(20)
        if not self.ready:
            print "Bot failed to get ready!"
            self.kill()

    def ping(self):
        self.waitingForPong = True
        self.push('PING')

class Master(object):
    def __init__(self):
        self.active = True
        self.networks = {}
        netinc = 1
        for num, i in enumerate(cfg.servers):
            print num, i
            self.networks[num+1] = Network(num+1, i['host'], self, i['chans'], i.get('auth', ''))
        self.workers = {}

        self.A = A
        self.A.master = self
        self.A.red = red
        self.A.loadMods(plugins)
        self.A.setConfig(cfg)

        thread.start_new_thread(self.pingLoop, ())

        self.sub = red.pubsub()
        self.sub.subscribe('irc.master')
        try: self.redLoop()
        except KeyboardInterrupt:
            for i in self.networks.values():
                i.quit()
        finally:
            self.sub.unsubscribe('irc.master')

    def addWorker(self, chan):
        #@DEV Find the network with the least workers
        m = (None, 100)
        for i in self.networks.values():
            if len(i.workers) < m[1]:
                m = (i, len(i.workers))
        w = m[0].getWorker()
        print 'Booting worker #%s' % w.id
        w.setup(chan)

    def redLoop(self):
        while True:
            for msg in self.sub.listen():
                try: m = json.loads(msg['data'])
                except: continue

                if m['tag'] == 'HI': self.addWorker(m['resp'])
                else: 
                    thread.start_new_thread(self.networks[m['nid']].workers[m['id']].parse, (m,)) #@DEV This may /not/ need to be threaded

    def pingLoop(self):
        st = time.time()
        while self.active:
            for i in self.networks.values():
                thread.start_new_thread(i.ping, ())
            time.sleep(60)

if __name__ == '__main__':
    master = Master()
   