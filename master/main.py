import redis, json, thread, time
from collections import deque #Deque is not required, it just makes things cleaner/nicer
from api import A

red = redis.Redis(host="hydr0.com", password="")
sub = red.pubsub()

server = "irc.quakenet.org"
channels = ["b0tt3st"]
plugins = ['web']
workers = {} #@TODO Ping workers to keep this in sync

def write(chan, msg):
    for i in workers.values():
        if chan.strip('#') in i.channels:
            i.write(chan, msg)
A.write = write

def pingloop():
    lastPing = time.time()
    while True:
        if time.time()-lastPing < 60: 
            time.sleep(5)
        else:
            for i in workers.values():
                i.send("PING")
                thread.start_new_thread(i.waitForPong, ())
            lastPing = time.time()

class Channel(object):
    def __init__(self, name):
        self.name = name
        self.nicks = {}
        self.topic = ""

    def isAdmin(): pass

    def addByName(self, name):
        if not isinstance(name, list):
            name = list(name)
        for i in name:
            if i in self.nicks: return
            op, voice = False, False
            if i.startswith('@'): op = True
            if i.startswith('+'): voice = True
            self.nicks[i] = {'op':op, 'voice':voice}
        
    def addByNick(self, nick):
        if nick in self.nicks: return
        self.nicks[nick] = {'op':False, 'voice':False}

    def rmvByNick(self, nick):
        if nick in self.nicks:
            del self.nicks[nick]

class Worker(object):
    def __init__(self):
        if len(workers.keys()):
            self.id = max(workers.keys())+1
        else: self.id = 1
        workers[self.id] = self
        self.nick = "B1nB0t-%s" % self.id
        self.chan = "irc.worker.%s" % self.id
        self.ready = False
        self.channels = deque()
        self.chans = {}

        self.server = server
        
        self.active = True
        self.ping = 0

    def setup(self, chan):
        red.publish(chan, json.dumps({
            'id':self.id,
            'channels':list(self.channels),
            'nick':self.nick,
            'server':self.server
        }))

    def parse(self, m):
        if 'chan' in m.keys():
            m['chan'] = m['chan'].lower()
        if m['tag'] == "BYE": 
            self.kill()
            self.send('NULL') #Run the worker loop once more
            del workers[self.id]
        elif m['tag'] == "MSG":
            print 'MSG: %s >> %s | %s' % (m['nick'], m['dest'], m['msg'])
            if A.parse(self, m): return
            if m['dest'].startswith('#'):
                A.fireHook('chanmsg', chan=m['dest'], user=m['nick'], msg=m['msg'], m=m['msg'].split(' '))
            else:
                A.fireHook('privmsg', user=m['nick'], msg=m['msg'], m=m['msg'].split(' '))
        elif m['tag'] == "NAMES":
            print 'NAMES: %s' % m['nicks']
            self.chans[m['chan']].addByName(m['nicks'])
        elif m['tag'] == "TOPIC":
            print 'TOPIC: %s' % m['topic']
            self.chans[m['chan']].topic = m['topic']
        elif m['tag'] == "JOIN":
            A.fireHook('join', user=m['nick'], chan=m['chan'])
            print 'JOIN: %s' % m['nick']
            self.chans[m['chan']].addByNick(m['nick'])
        elif m['tag'] == "PART":
            A.fireHook('part', user=m['nick'], chan=m['chan'], msg=m['msg'])
            print 'PART: %s' % m['nick']
            self.chans[m['chan']].rmvByNick(m['nick'])
        elif m['tag'] == "READY":
            self.ready = True
            w.getChannels()
        elif m['tag'] == "PONG":
            self.waitingForPong = False
        else:
            print m

    def write(self, chan, msg):
        self.send('MSG', chan=chan, msg=msg) 

    def send(self, tag, **kwargs):
        kwargs['tag'] = tag
        red.publish(self.chan, json.dumps(kwargs)) #@DEV If we want, we can eventually zlib this

    def kill(self):
        if len(workers.values()) > 1: #Distribute channels to other workers
            for i in workers.values():
                if i != self:
                    if not len(self.channels): break
                    i.addChannel([self.channels.popleft()])
        self.active = False

    def refreshChans(self):
        for i in self.channels:
            i = "#"+i.lower()
            if i not in self.chans.keys():
                self.chans[i] = Channel(i)

    def addChannel(self, chans): #Chans is a list
        self.channels += chans
        self.send("JOIN", chans=['#'+i for i in chans])
        self.refreshChans()

    def rmvChannel(self, chan):
        if chan in self.channels:
            self.channels.pop(self.channels.index(chan))
        self.send("LEAVE", chans=['#'+chan], msg="Bot swap...")

    def getChannels(self):
        global channels, workers
        if len(workers) == 1: self.addChannel(channels)
        else:
            c = len(channels)/len(workers.values()) #If we have more workers then channels, we wont get a channel
            for i in workers.values():
                if not c: break
                chan = i.channels.popleft()
                self.addChannel([chan]) #Popleft() gets us the FIRST joined channel, which should keep joins/parts to a minimum (on some level)
                i.rmvChannel(chan)
                c -= 1
        self.refreshChans()

    def waitForReady(self):
        st = time.time()
        while time.time()-st < 20: #Wait ten seconds for the bot to connect
            if self.ready: return
            time.sleep(.5)
        print "Bot failed to get ready!"
        self.kill()

    def waitForPong(self):
        st = time.time()
        self.waitingForPong = True
        while time.time()-st < 15:
            time.sleep(.5)
            if not self.waitingForPong: return
        print 'Worker PONG timed out!'
        self.kill()

if __name__ == '__main__':
    thread.start_new_thread(pingloop, ())
    A.loadMods(plugins)
    try:
        sub.subscribe('irc.master')
        while True:
            for msg in sub.listen():
                #print msg #@DEV Debug
                try: m = json.loads(msg['data'])
                except: 
                    print msg
                    continue
                if m['tag'] == 'HI':
                    w = Worker()
                    w.setup(m['resp'])
                    thread.start_new_thread(w.waitForReady, ())
                    #red.publish(m['resp'], json.dumps({'id':w.id, 'chan')
                else:
                    workers[m['id']].parse(m)
    except KeyboardInterrupt:
        for i in workers.values():
            i.send("SHUTDOWN")
    finally:
        sub.unsubscribe('irc.master')