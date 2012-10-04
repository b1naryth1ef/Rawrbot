from connection import Connection
from collections import deque
import redis, json
import random, thread
import sys

class Worker(object):
    def __init__(self):
        self.id = -1
        self.nick = ""
        self.channels = []
        self.server = ""

        self.c = Connection()
        self.red = redis.Redis(host="hydr0.com", password="")
        self.sub = self.red.pubsub()

        self.nickq = {}
        self.sends = deque()

        try:
            self.boot()
            self.active = True
            thread.start_new_thread(self.ircloop, ())
            self.redloop()
        except:
           self.quit()

    def parse(self, msg):
        m = msg.split(' ', 2)
        if m[0] == "PING": self.c.write('PONG')
        if "@" not in m[0]:
            if m[1] == "353": #NAMES
                m = m[2].split(' ', 3)
                chan = m[2]
                nicks = m[3][1:].split(' ')
                if chan not in self.nickq.keys(): self.nickq[chan] = nicks
                else: self.nickq[chan] += nicks
            elif m[1] == "366": #END OF NAMES
                m = m[2].split(' ', 2)
                self.push('NAMES', chan=m[1], nicks=self.nickq[m[1]])
            elif m[1] == "332": #TOPIC
                m = msg.split(' ')
                self.push('TOPIC', chan=m[3], topic=m[-1][1:])
        else:
            nick, host = m[0].split('!')
            nick = nick[1:]
            if m[1] == "JOIN":
                if nick.lower() == self.nick.lower(): pass
                else: self.push('JOIN', nick=nick, chan=m[2])
            elif m[1] == "PART": #@TODO add msg parsing
                if nick.lower() == self.nick.lower(): pass
                else: self.push('PART', nick=nick, chan=m[2], msg="")
            elif m[1] == "PRIVMSG":
                m = msg.split(' ', 3)
                dest = m[2]
                msg = m[3][1:]
                self.push("MSG", dest=dest, msg=msg, nick=nick, host=host)
        
    def redloop(self):
        print 'Looping redis'
        self.rsub = self.red.pubsub()
        self.rsub.subscribe("irc.worker.%s" % self.id)
        while self.active:
            for msg in self.rsub.listen():
                print ">>>", msg
                try: m = json.loads(msg['data'])
                except: 
                    print msg
                    continue
                if m['tag'] == "LEAVE":
                    self.c.write('PART %s %s' % (m['chan'], m['msg']))  
                elif m['tag'] == "JOIN":
                    self.c.write('JOIN %s' % m['chan'])
                elif m['tag'] == "SHUTDOWN":
                    self.quit("Bot is shutting down...", True)
                elif m['tag'] == "PING":
                    self.push('PONG')
                elif m['tag'] == "MSG":
                    self.c.write('PRIVMSG %s :%s' % (m['chan'], m['msg'])) 
        self.rsub.unsubscribe("irc.worker.%s" % self.id)

    def ircloop(self):
        print 'Connecting...'
        self.c.host = self.server
        self.c.nick = self.nick
        self.c.connect(self.channels)
        self.push('READY')
        while self.active:
            l = self.c.read()
            for i in l.split('\r\n'):
                if i:
                    print i
                    self.parse(i)

    def quit(self, reason="Bot is leaving..."):
        self.c.write('QUIT :%s' % reason)
        self.push('BYE')
        self.active = False
        sys.exit()
        #self.red.disconnect()

    def boot(self):
        print 'Attempting to boot worker...'
        resp = "irc.%s" % random.randint(1111, 9999) #Get a random channel int
        self.sub.subscribe(resp)
        self.push("HI", resp=resp)
        while True:
            for msg in self.sub.listen():
                try: obj = json.loads(msg['data'])
                except:
                    print msg
                    continue
                self.__dict__.update(obj)
                print 'Got worker info:', obj
                break
            break
        self.sub.unsubscribe(resp)

    def push(self, tag, **kwargs): #Push a message to master
        kwargs['tag'] = tag
        kwargs['id'] = self.id
        self.red.publish("irc.master", json.dumps(kwargs))

w = Worker()
