import redis, json, thread, time
from collections import OrderedDict
from api import A

red = redis.Redis(host="hydr0.com", password="")
plugins = ['web']

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
    def __init__(self, id, name, master, channels=[]):
        self.id = id
        self.name = name
        self.master = master

        self.channels = OrderedDict([(i, Channel(self, i)) for i in channels]) #NAME :> CHANNEL
        self.workers = {}

    def addWorker(self, worker):
        self.workers[worker.id] = worker
        #self.workers[worker.id].getChannels() #@DEV This is done when we're ready

    def rmvWorker(self, wid):
        del self.workers[wid]

    def quit(self):
        for i in self.workers.values():
            i.push('SHUTDOWN')

    def ping(self):
        for worker in self.workers.values():
            worker.ping()
        time.sleep(15)
        for worker in self.workers.values():
            if worker.waitingForPong:
                print "Worker #%s timed out on pong!" % worker.id
                worker.kill()

class Worker(object):
    def __init__(self, wid, network):
        self.id = wid
        self.network = network
        self.A = self.network.master.A
        self.channels = []

        self.ready = False
        self.active = True
        self.waitingForPong = False

    def setup(self, chan):
        self.nick = "RawrBot-%s" % self.id
        self.chan = "irc.worker.%s" % self.id
        self.network.addWorker(self)
        red.publish(chan, json.dumps({
            'id':self.id,
            'channels':list(self.channels),
            'nick':self.nick,
            'server':self.network.name,
            'nid':self.network.id
        }))
        thread.start_new_thread(self.waitForReady, ())

    def getChan(self, name):
        return self.network.channels[name]

    def parse(self, m):
        if 'chan' in m.keys():
            m['chan'] = m['chan'].replace('#', '')

        if m['tag'] == "BYE": 
            self.kill()
        elif m['tag'] == "MSG":
            print 'MSG: %s >> %s | %s' % (m['nick'], m['dest'], m['msg'])
            if self.A.parse(self, m): return
            if m['dest'].startswith('#'):
                self.A.fireHook('chanmsg', chan=m['dest'].replace('#', ''), user=m['nick'], msg=m['msg'], m=m['msg'].split(' '), w=self)
            else:
                self.A.fireHook('privmsg', user=m['nick'], msg=m['msg'], m=m['msg'].split(' '), w=self)
        elif m['tag'] == "NAMES": self.getChan(m['chan']).addByNames(m['nicks'])
        elif m['tag'] == "TOPIC": self.getChan(m['chan']).setTopic(m['topic'])
        elif m['tag'] == "JOIN":
            self.A.fireHook('join', user=m['nick'], chan=m['chan'], w=self)
            self.getChan(m['chan']).addByNick(m['nick'])
        elif m['tag'] == "PART":
            self.A.fireHook('part', user=m['nick'], chan=m['chan'], msg=m['msg'], w=self)
            self.getChan(m['chan']).rmvByNick(m['nick'])
        elif m['tag'] == "READY":
            self.ready = True
            self.getChannels()
        elif m['tag'] == "PONG": self.waitingForPong = False
        else: print m

    def getChannels(self): #@TODO Implement more bots per channel
        num = (len(self.network.channels)/len(self.network.workers))

        if len(self.network.workers) > 1:
            for i in range(0, num):
                for i in self.network.workers.values():
                    if i == self: continue
                    if num > 0: num -= 1
                    else: return
                    c = i.channels.pop(0)
                    i.partChannel(c, ing=True)
                    self.joinChannel(c)
        else:
            for i in self.network.channels.values():
                self.joinChannel(i)

    def write(self, chan, msg): 
        if isinstance(chan, Channel):
            chan = chan.name
        self.push('MSG', chan='#'+chan, msg=msg) 

    def push(self, tag, **kwargs):
        kwargs['tag'] = tag
        red.publish(self.chan, json.dumps(kwargs)) #@DEV If we want, we can eventually zlib this

    def kill(self):
        print 'Worker #%s is going down.' % self.id
        self.network.master.rmvWorker(self.id)
        self.network.rmvWorker(self.id)
        self.active = False

    def joinChannel(self, chan):
        if isinstance(chan, Channel):
            chan = chan.name
        self.channels.append(chan)
        self.push("JOIN", chan="#"+chan)

    def partChannel(self, chan, msg="Bot Swap...", ing=False):
        if isinstance(chan, Channel):
            chan = chan.name
        if not ing:
            self.channels.pop(self.channels.index(chan))
        self.push("LEAVE", chan="#"+chan, msg=msg)

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
        self.networks = {
            #'quakenet':Network(1, 'irc.quakenet.org', self, ['b0tt3st']),
            'esper':Network(2, 'irc.esper.net', self, ['b0tt3st', 'Testy1', 'Testy2', 'Testy3'])
        }
        self.workers = {}

        self.A = A
        self.A.loadMods(plugins)

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

        #@DEV What ID are we?
        w = Worker(1, m[0])
        if len(self.workers): #@TODO Fix this shit
            p = -1
            if None in self.workers.values():
                for pos in self.workers:
                    if self.workers[pos] == None:
                        p = pos
                        break
            else:
                p = max(self.workers.keys())+1
                print 'Added worker %s' % p
            self.workers[p] = w
            w.id = p
        else:
            self.workers[1] = w
        
        w.setup(chan)

    def rmvWorker(self, wid):
        del self.workers[wid]
        self.workers[wid] = None

    def redLoop(self):
        while True:
            for msg in self.sub.listen():
                try: m = json.loads(msg['data'])
                except: continue

                if m['tag'] == 'HI': self.addWorker(m['resp'])
                else:
                    self.workers[m['id']].parse(m)

    def pingLoop(self):
        st = time.time()
        while self.active:
            for i in self.networks.values():
                thread.start_new_thread(i.ping, ())
            time.sleep(60)

master = Master()