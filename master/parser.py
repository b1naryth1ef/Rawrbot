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
                    if nickkey in i: #@TODO Cleanup
                        if i.startswith('@'):
                            id = int(i.split(nickkey)[-1])
                            self.red.set('i.%s.worker.%s.%s.ops' % (q['nid'], id, q['chan']), True)
                        continue #@NOTE We dont count ourselves
                    if i[0] == '@':
                        i = i[1:].lower()
                        self.red.sadd('i.%s.chan.%s.ops' % (q['nid'], q['chan']), i)
                    elif i[0] == '+': i = i[1:].lower()
                    self.red.sadd('i.%s.chan.%s.users' % (q['nid'], q['chan']), i.lower())
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
        elif q['tag'] == 'MODEC':
            if q['mode'][0] in ['+', '-']:
                self.A.fireEvent('CHANNEL_MODE', modetype=q['mode'][0], **q)
        elif q['tag'] == 'MODEU':
            nickkey = self.red.get('i.%s.nickkey' % q['nid'])
            if q['mode'][0] in ['+', '-']:
                if 'o' in q['mode']:
                    if nickkey and nickkey in q['target']:
                        if q['mode'][0] == '+':
                            id = int(q['target'].split(nickkey)[-1])
                            self.red.set('i.%s.worker.%s.%s.ops' % (q['nid'], id, q['chan']), True)
                        else:
                            id = int(q['target'].split(nickkey)[-1])
                            self.red.set('i.%s.worker.%s.%s.ops' % (q['nid'], id, q['chan']), False)
                    if q['mode'][0] == '-': self.red.srem('i.%s.chan.%s.ops' % (q['nid'], q['chan']), q['target'].lower())
                    else: self.red.sadd('i.%s.chan.%s.ops'% (q['nid'], q['chan']), q['target'].lower())
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