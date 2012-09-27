import redis, json
from collections import deque #Deque is not required, it just makes things cleaner/nicer

red = redis.Redis(host="hydr0.com", password="")
sub = red.pubsub()

server = "irc.quakenet.org"
channels = ["B0tT3st3r", "Test1", "Test2"]
workers = [] #@TODO Ping workers to keep this in sync

class Worker(object):
    def __init__(self):
        workers.append(self)
        self.id = len(workers)
        self.nick = "B1nB0t-%s" % self.id
        self.chan = "irc.worker.%s" % self.id
        self.channels = deque()

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

    def parse(self, msg):
        m = json.loads(msg)
        if m['tag'] == "BYE": self.kill()

    def send(self, tag, **kwargs):
        kwargs['tag'] = tag
        red.publish(self.chan, json.dumps(kwargs)) #@DEV If we want, we can eventually zlib this

    def kill(self):
        if len(workers) > 1: #Distribute channels to other workers
            for i in workers:
                if i != self:
                    i.addChan(self.channels.popleft())

        self.active = False
        workers.pop(self.id)

    def addChannel(self, chans): #Chans is a list
        self.channels += chans
        self.send("JOIN", chans=chans)

    def getChannels(self):
        global channels, workers
        if len(workers) == 1: self.addChannel(channels)
        else:
            c = len(channels)/len(workers) #If we have more workers then channels, we wont get a channel
            for i in workers:
                if not c: break
                self.addChannel([i.channels.popleft()]) #Popleft() gets us the FIRST joined channel, which should keep joins/parts to a minimum (on some level)
                c -= 1

sub.subscribe('irc.master')
while True:
    for msg in sub.listen():
        print msg #@DEV Debug
        m = json.loads(msg['data'])
        if m['tag'] == 'HI':
            w = Worker()
            w.getChannels()
            w.setup(m['resp'])
            #red.publish(m['resp'], json.dumps({'id':w.id, 'chan')
sub.unsubscribe('irc.master')