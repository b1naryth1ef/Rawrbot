from connection import Connection
from collections import deque
import redis, json
import random, thread
import sys, os, time

class Worker(object):
    def __init__(self):
        self.id = -1
        self.nid = -1
        self.nick = ""
        self.channels = []
        self.whois = {}
        self.auth = ""
        self.server = ""
        self.ready = False
        self.readyq = deque()
        self.lastwrite = 0
        self.pinged = False

        self.red = redis.Redis(host="hydr0.com", password="")
        self.sub = self.red.pubsub()

        self.nickq = {}

        try:
            self.boot()
            self.active = True
            
            self.connect()
            thread.start_new_thread(self.ircloop, ())
            self.redloop()
        except:
           self.quit()

    def getChanReads(self, *args):
        return ['i.%s.chan.%s' % (self.nid, i.replace('#', '')) for i in self.channels]+list(args)

    def parse(self, msg):
        m = msg.split(' ', 2)
        if m[0] == "PING": return self.c.write('PONG')
        print msg
        if "@" not in m[0]:
            if m[1] == "353": #NAMES
                m = m[2].split(' ', 3)
                chan = m[2]
                nicks = m[3][1:].split(' ')
                if chan not in self.nickq.keys(): self.nickq[chan] = nicks
                else: self.nickq[chan] += nicks
            elif m[1] == "366": #END OF NAMES
                m = m[2].split(' ', 2)
                self.p('NAMES', chan=m[1], nicks=self.nickq[m[1]])
            elif m[1] == "332": #TOPIC
                m = msg.split(' ')
                self.p('TOPIC', chan=m[3], topic=m[-1][1:])
            elif m[1] == '311': #WHOIS user info
                m = msg.split(' ')
                nick = m[3]
                host = m[5]
                if nick.lower() in self.whois.keys():
                    self.whois[nick.lower()]['nick'] = nick.lower()
                    self.whois[nick.lower()]['host'] = host
            elif m[1] == '330':
                m = msg.split(' ')
                nick = m[3]
                authname = m[4]
                if nick.lower() in self.whois.keys():
                    self.whois[nick.lower()]['auth'] = authname
            elif m[1] == '318': #END OF WHOIS
                m = msg.split(' ')
                if m[3].lower() in self.whois.keys():
                    print 'Got end of whois, sending...'
                    self.red.lpush(self.whois[m[3].lower()]['chank'], json.dumps(self.whois[m[3].lower()]))
                    del self.whois[m[3].lower()]
        else:
            nick, host = m[0].split('!')
            nick = nick[1:]
            if m[1] == "JOIN":
                if nick.lower() == self.nick.lower(): pass
                else:
                    self.p('JOIN', nick=nick, chan=m[2])
            elif m[1] == "PART": #@TODO add msg parsing
                if nick.lower() == self.nick.lower(): pass
                else: 
                    chan = m[2].split(':')[0]
                    self.p('PART', nick=nick, chan=chan, msg="")
            elif m[1] == "PRIVMSG":
                m = msg.split(' ', 3)
                dest = m[2]
                msg = m[3][1:]
                self.p("MSG", dest=dest, msg=msg, nick=nick, host=host)
            elif m[1] == "KICK":
                m = msg.split(' ', 4)
                chan = m[2]
                kicked = m[3]
                if kicked == self.nick: us = True
                else: us = False
                msg = m[4][1:]
                self.p('KICK', chan=chan, msg=msg, kicked=kicked, nick=nick, host=host, us=us)


    def p(self, tag, **kwargs): #Any master can parse a message pushed here
        kwargs['tag'] = tag
        kwargs['id'] = self.id
        kwargs['nid'] = self.nid
        self.red.rpush('i.parseq', json.dumps(kwargs))

    def write(self, *args, **kwargs):
        self.c.write(*args, **kwargs)

    def join(self, chan):
        print 'Joining %s' % chan
        if not chan.startswith('#'): chan = "#"+chan
        self.channels.append(chan)
        self.write('JOIN %s' % chan)

    def part(self, chan, msg="Leaving"):
        if not chan.startswith('#'): chan = "#"+chan
        if chan not in self.channels: return
        self.channels.remove(chan)
        self.write('PART %s :%s' % (chan, msg))  

    def redloop(self):
        print 'Looping redis'
        while self.active:
            c, q = self.red.blpop(self.getChanReads('i.%s.worker.%s' % (self.nid, self.id)))
            try: q = json.loads(q)
            except:
                print "Bad message: %s" % msg
                continue
            if q['tag'] == 'PART': self.part(q['chan'], q['msg'])
            elif q['tag'] == 'JOIN': self.join(q['chan'])
            elif q['tag'] == "SHUTDOWN": self.quit(q['msg'])
            elif q['tag'] == "PING": 
                self.pinged = True
                self.push('PONG')
            elif q['tag'] == "MSG": self.write('PRIVMSG #%s :%s' % (q['chan'], q['msg']))
            elif q['tag'] == "PM": self.write('PRIVMSG %s :%s' % (q['nick'], q['msg']))
            elif q['tag'] == 'WHOIS':
                if q['nick'] not in self.whois.keys():
                    self.whois[q['nick'].lower()] = {'chank':q['chan']}
                    self.write('WHOIS %s' % (q['nick']))
            elif q['tag'] == 'ID':
                print 'Recovering from master failure!'
                for i in self.channels:
                    self.write('PRIVMSG %s :%s' % (i, 'Master has gone down! Bot is recovering...'))
                self.push('ID', id=self.id, nid=self.nid, chans=self.channels)
            else:
                print 'WAT? %s: %s' % (c, q)
            #@TODO Add a delay here depending on the server

    def connect(self):
        print 'Connecting to %s as %s' % (self.server, self.nick)
        self.c = Connection(host=self.server, nick=self.nick)
        if self.auth:
            self.c.joins.append(self.auth)
            self.c.joins.append('MODE %s +x' % self.nick)
        if not self.c.connect(self.channels):
            print 'Failed to connect!'
            sys.exit()
        self.push('READY')
        self.ready = True
        for i in self.readyq:
            i = self.readyq.popleft()
            self.c.write(*i[0], **i[1])

    def ircloop(self):
        while self.active and self.c.alive:
            l = self.c.read()
            for i in l.split('\r\n'):
                if i: self.parse(i)
                #else: print "Did we get disconnected from irc?"

    def quit(self, reason="Bot is leaving..."):
        print 'Bot is quitting!'
        if self.c.alive: 
            self.write('QUIT :%s' % reason)
            self.c.disconnect()
        self.push('BYE')
        self.active = False
        sys.exit()

    def boot(self):
        print 'Attempting to boot worker!'
        resp = "irc.%s" % random.randint(1111, 9999) #Get a random channel int
        self.sub.subscribe(resp)
        self.push("HI", resp=resp)
        while True:
            for msg in self.sub.listen():
                try: obj = json.loads(msg['data'])
                except:
                    print msg
                    continue
                self.__dict__.update(obj) #@TODO Fix this
                print 'Got worker info:', obj
                break
            break
        self.sub.unsubscribe(resp)

    def push(self, tag, **kwargs): #Push a message to master
        kwargs['tag'] = tag
        kwargs['id'] = self.id
        if tag != 'HI': kwargs['nid'] = self.nid
        self.red.publish("irc.master", json.dumps(kwargs))

w = Worker()
