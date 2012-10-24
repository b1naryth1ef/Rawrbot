import json, thread
import api

class Parser(object):
    def __init__(self, master, red, a):
        self.master = master
        self.red = red
        self.A = a
        self.A.master = master
        self.A.loadPlugins()

    def takeMaster(self):
        self.A.canLoop = True
        self.A.loadLoops()

    def write(self, chan): pass

    def parse(self, q):
        if q['tag'] == "MSG":
            if q['msg'].startswith(self.A.prefix) and q['msg'][1] != ' ': 
                if self.A.parseCommand(q): return
            self.A.fireEvent('CHANMSG', q)
        elif q['tag'] == 'NAMES':
            nickkey = self.red.get('i.%s.nickkey' % q['nid'])
            if nickkey:
                for i in q['nicks']:
                    if nickkey in i: continue #@NOTE We dont count ourselves
                    if i[0] in ['@', '+']: i = i[1:]
                    self.red.sadd('i.%s.chan.%s.users' % (q['nid'], q['chan'].replace('#', '')), i.lower())
        elif q['tag'] == 'TOPIC': pass
        elif q['tag'] == 'JOIN':
            nickkey = self.red.get('i.%s.nickkey' % q['nid'])
            if nickkey in q['nick']: return
            self.red.sadd('i.%s.chan.%s.users' % (q['nid'], q['chan'].replace('#', '')), q['nick'].lower())
        elif q['tag'] == 'PART':
            self.red.srem('i.%s.chan.%s.users' % (q['nid'], q['chan'].replace('#', '')), q['nick'].lower())
        elif q['tag'] == 'KICK':
            if q['us']:
                m = {'tag':'JOIN', 'chan':q['chan']}
                self.red.rpush('i.%s.worker.%s' % (q['nid'], q['id']), json.dumps(m))
            self.red.srem('i.%s.chan.%s.users' % (q['nid'], q['chan'].replace('#', '')), q['nick'].lower())

    def parseLoop(self):
        while True:
            c, q = self.red.blpop('i.parseq')
            try:
                q = json.loads(q)
            except:
                print 'Parser failed on', q
                continue
            print q
            thread.start_new_thread(self.parse, (q,))