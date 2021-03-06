from connection import Connection
from collections import deque
import redis, json
import random, thread
import sys, time, os

class Worker(object):
    def __init__(self):
        self.id = -1
        self.nid = -1
        self.nick = ""
        self.ready = False
        self.keepAlive = True
        self.readyq = deque()
        self.channels = []

        #Queued Responses
        self.whois = {}
        self.nickq = {}

        #Server Info
        self.auth = ""
        self.server = ""

        #Pong Tracking
        self.lastPong = 0
        self.pinged = False

        self.red = redis.Redis(host="hydr0.com", password=os.getenv("REDISPASS"))

        while self.keepAlive:
            print 'Starting Loop!'
            try:
                self.sub = self.red.pubsub()
                self.boot()
                self.connect()
                thread.start_new_thread(self.ircloop, ())
                self.redloop()
            except KeyboardInterrupt:
                self.quit("Keyboard Interrupt (killed)")
                sys.exit()
            except Exception, e:
                self.quit('Exception running! (%s)' % e)
                time.sleep(30) #buffer reconnects

    def checkForPing(self):
        while self.active:
            self.pinged = False
            time.sleep(60)
            if not self.pinged:
                print "Master has not pinged us, going down!"
                self.keepAlive = False
                self.quit("Master ping-out")

    def getChanReads(self, *args):
        return ['i.%s.chan.%s' % (self.nid, i.replace('#', '').lower()) for i in self.channels]+list(args)

    def sendNames(self, chan, names):
        self.p('NAMES', chan=chan, nicks=names)

    def parse(self, msg): #@TODO Clean this up
        m = msg.split(' ', 2)
        if m[0] == "PING":
            self.lastPong = time.time()
            return self.c.write('PONG')
        #print msg
        if "@" not in m[0] and len(m) > 1:
            if m[1] == "353": #NAMES
                m = m[2].split(' ', 3)
                chan = m[2]
                nicks = m[3][1:].split(' ')
                if chan not in self.nickq.keys(): self.nickq[chan] = nicks
                else:
                    if self.nickq[chan] == 0: #This gets around stupid packet shuffling
                        self.sendNames(chan, nicks)
                    else: self.nickq[chan] += nicks
            elif m[1] == "366": #END OF NAMES
                m = m[2].split(' ', 2)
                if m[1] not in self.nickq.keys():
                    self.nickq[m[1]] = 0
                    return
                self.sendNames(m[1], self.nickq[m[1]])
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
                    self.whois[nick.lower()]['auth'] = authname.lower()
            elif m[1] == '318': #END OF WHOIS
                m = msg.split(' ')
                print m
                if m[3].lower() in self.whois.keys():
                    self.p('WHOIS', **self.whois[m[3].lower()])
                    del self.whois[m[3].lower()]
            elif m[1] == '474':
                m = msg.split('', 4)
                self.p('BANNED', chan=m[3], nick=m[2], msg=m[4])

        elif len(m) > 1:
            nick, host = m[0].split('!')
            nick = nick[1:]
            if m[1] == "JOIN":
                if nick.lower() == self.nick.lower(): pass
                else: self.p('JOIN', nick=nick, chan=m[2])
                self.getWhois(nick)
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
            elif m[1] == 'MODE':
                m = msg.split(' ', 4)
                if len(m) == 4:
                    self.p('MODEC', chan=m[2], mode=m[3], nick=nick, host=host)
                elif len(m) == 5:
                    self.p('MODEU', target=m[4], chan=m[2], mode=m[3], nick=nick, host=host)
            elif m[1] == 'NICK':
                self.p('NICK', nick=nick, host=host, newnick=m[2][1:])
            elif m[1] == 'QUIT':
                self.p('QUIT', nick=nick, host=host, msg=m[2][1:])

    def p(self, tag, **kwargs): #Any master can parse a message pushed here
        kwargs['tag'] = tag
        kwargs['id'] = self.id
        kwargs['nid'] = self.nid
        self.red.rpush('i.parseq', json.dumps(kwargs))

    def write(self, *args, **kwargs):
        self.c.write(*args, **kwargs)

    def join(self, chan, pw=None):
        print 'Joining %s' % chan
        if not chan.startswith('#'): chan = "#"+chan
        self.channels.append(chan)
        self.write('JOIN %s %s' % (chan, pw))

    def part(self, chan, msg="Leaving"):
        if not chan.startswith('#'): chan = "#"+chan
        if chan not in self.channels: return
        self.channels.remove(chan)
        self.write('PART %s :%s' % (chan, msg))

    def getWhois(self, nick):
        nick = nick.lower()
        if nick not in self.whois.keys():
            self.whois[nick] = {}
            self.write('WHOIS %s' % (nick))

    def redloop(self):
        print 'Looping redis'
        while self.active:
            c, q = self.red.blpop(self.getChanReads('i.%s.worker.%s' % (self.nid, self.id)))
            try: q = json.loads(q)
            except:
                print "Bad message: %s" % q
                continue
            print q
            if q['tag'] != 'PING': print '[%s] => %s' % (q['tag'], q)
            if q['tag'] == 'PART': self.part(q['chan'], q['msg'])
            elif q['tag'] == 'JOIN': self.join(q['chan'], q['pw'])
            elif q['tag'] == "SHUTDOWN": self.quit(q['msg'])
            elif q['tag'] == "PING":
                self.pinged = True
                self.push('PONG')
            elif q['tag'] == 'RAW':
                self.write(q['msg'])
            elif q['tag'] == "MSG": self.write('PRIVMSG #%s :%s' % (q['chan'], q['msg']))
            elif q['tag'] == "PM": self.write('PRIVMSG %s :%s' % (q['nick'], q['msg']))
            elif q['tag'] == 'WHOIS':
                self.getWhois(q['nick'].lower())
            elif q['tag'] == 'ID':
                print 'Master failed!'
                self.push('ID', id=self.id, nid=self.nid, chans=self.channels)
                self.pinged = True #Reset ping loop to fix edge case
            else:
                print 'WAT? %s: %s' % (c, q)

    def connect(self):
        print 'Connecting to %s as %s' % (self.server, self.nick)
        self.c = Connection(host=self.server, nick=self.nick)
        if self.auth:
            self.c.joins.append(self.auth)
            self.c.joins.append('MODE %s +x' % self.nick)
        if not self.c.connect(self.channels):
            print 'Failed to connect!'
            sys.exit()
        print 'CONNECTED!'
        self.push('READY')
        thread.start_new_thread(self.checkForPing, ())
        self.ready = True
        self.lastPong = time.time()
        for i in self.readyq:
            i = self.readyq.popleft()
            self.c.write(*i[0], **i[1])

    def ircloop(self):
        while self.active and self.c.alive:
            l = self.c.read()
            if not l: return self.quit("Disconnected from irc!")
            for i in l.split('\r\n'):
                if i: thread.start_new_thread(self.parse, (i,)) #Not really required, but helps safe-handeling functions (for now)

    def quit(self, reason="Bot is leaving..."):
        print 'Bot is quitting! (%s)' % reason
        if self.c.alive:
            self.write('QUIT :%s' % reason)
            self.c.disconnect()
        self.push('BYE')
        self.active = False

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
                self.active = True
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
