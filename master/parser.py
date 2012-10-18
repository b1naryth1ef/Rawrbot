import json, thread
import api

class Parser(object):
    def __init__(self, red, a):
        self.red = red
        self.A = a
        self.A.loadPlugins()

    def write(self, chan): pass

    def parse(self, q):
        if q['tag'] == "MSG":
            if q['msg'].startswith(self.A.prefix): 
                if self.A.parseCommand(q): return
            self.A.fireEvent('CHANMSG', q)
        elif q['tag'] == 'NAMES':
            nickkey = self.red.get('i.%s.nickkey' % q['nid'])
            if nickkey:
                k = {}
                for i in q['nicks']:
                    if nickkey in i: continue #@NOTE We dont count ourselves
                    if i.startswith('+'): k[i[1:]] = 1
                    elif i.startswith('@'): k[i[1:]] = 2
                    else: k[i] = 0
                if len(k):
                    self.red.zadd('i.%s.chan.%s.users' % (q['nid'], q['chan'].replace('#', '')), **k)
        elif q['tag'] == 'TOPIC': pass
        elif q['tag'] == 'JOIN': pass
        elif q['tag'] == 'PART': pass

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