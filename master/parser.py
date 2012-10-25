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
        if 'chan' in q:
            q['chan'] = q['chan'].replace('#', '').lower()
        if q['tag'] == "MSG":
            if q['msg'].startswith(self.A.prefix) and q['msg'][1] != ' ': 
                if self.A.parseCommand(q): return
            self.A.fireEvent('CHANMSG', **q)
        elif q['tag'] == 'NAMES':
            nickkey = self.red.get('i.%s.nickkey' % q['nid'])
            if nickkey:
                for i in q['nicks']:
                    if nickkey in i: 
                        if i.startswith('@'):
                            id = int(i.split(nickkey)[-1])
                            self.red.sadd('i.%s.worker.%s.ops')
                        continue #@NOTE We dont count ourselves
                    if i[0] in ['@', '+']: i = i[1:]
                    self.red.sadd('i.%s.chan.%s.users' % (q['nid'], q['chan'], i.lower()))
        elif q['tag'] == 'TOPIC': pass
        elif q['tag'] == 'JOIN':
            nickkey = self.red.get('i.%s.nickkey' % q['nid'])
            if nickkey in q['nick']: return
            self.red.sadd('i.%s.chan.%s.users' % (q['nid'], q['chan']), q['nick'].lower())
            self.A.fireEvent('JOIN', nick=q['nick'].lower(), chan=q['chan'], nid=q['nid'], wid=q['wid'])
        elif q['tag'] == 'PART':
            self.red.srem('i.%s.chan.%s.users' % (q['nid'], q['chan']), q['nick'].lower())
            self.A.fireEvent('PART', nick=q['nick'].lower(), chan=q['chan'], msg=q['msg'], nid=q['nid'], wid=q['wid'])
        elif q['tag'] == 'KICK':
            q['kicked'] = q['kicked'].lower()
            q['nick'] = q['nick'].lower()
            if q['us']:
                m = {'tag':'JOIN', 'chan':q['chan'], 'pw':self.red.get('i.%s.chan.%s.pw' % (q['nid'], q['chan']))}
                self.red.rpush('i.%s.worker.%s' % (q['nid'], q['id']), json.dumps(m))
                return self.A.fireEvent('KICK_W', **q)
            self.A.fireEvent('KICK', **q)
            self.red.srem('i.%s.chan.%s.users' % (q['nid'], q['chan']), q['nick'].lower())
        elif q['tag'] == 'MODE': pass

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