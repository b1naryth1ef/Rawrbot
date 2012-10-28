import json, thread

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
        elif q['tag'] == 'NAMES': #@TODO Cleanup
            nickkey = self.red.get('i.%s.nickkey' % q['nid'])
            if nickkey:
                for i in q['nicks']:
                    print 'USER:', i
                    if nickkey in i:
                        if i.startswith('@'):
                            id = int(i[-1])
                            self.red.set('i.%s.worker.%s.%s.op' % (q['nid'], id, q['chan']), 1)
                            print "Bot is an op: %s/%s" % (i, q['chan'])
                        continue #@NOTE We dont count ourselves
                    if i[0] == '@':
                        i = i[1:].lower()
                        self.red.sadd('i.%s.chan.%s.ops' % (q['nid'], q['chan']), i)
                        print 'User is op: %s/%s' % (i, q['chan'])
                    elif i[0] == '+': i = i[1:].lower()
                    self.red.sadd('i.%s.chan.%s.users' % (q['nid'], q['chan']), i.lower())
        elif q['tag'] == 'TOPIC': pass
        elif q['tag'] == 'JOIN':
            nickkey = self.red.get('i.%s.nickkey' % q['nid'])
            if nickkey in q['nick']: return
            self.red.sadd('i.%s.chan.%s.users' % (q['nid'], q['chan']), q['nick'].lower())
            self.A.fireEvent('JOIN', nick=q['nick'].lower(), chan=q['chan'], nid=q['nid'], id=q['id'])
        elif q['tag'] == 'PART':
            self.red.srem('i.%s.chan.%s.users' % (q['nid'], q['chan']), q['nick'].lower())
            self.red.srem('i.%s.chan.%s.ops' % (q['nid'], q['chan']), q['nick'].lower()) #@NOTE We dont care if this works/doesnt
            self.A.fireEvent('PART', nick=q['nick'].lower(), chan=q['chan'], msg=q['msg'], nid=q['nid'], id=q['id'])
        elif q['tag'] == 'KICK':
            q['kicked'] = q['kicked'].lower()
            q['nick'] = q['nick'].lower()
            if q['us']:
                m = {'tag':'JOIN', 'chan':q['chan'], 'pw':self.red.get('i.%s.chan.%s.pw' % (q['nid'], q['chan']))}
                self.red.rpush('i.%s.worker.%s' % (q['nid'], q['id']), json.dumps(m))
                return self.A.fireEvent('KICK_W', **q)
            self.A.fireEvent('KICK', **q)
            self.red.srem('i.%s.chan.%s.users' % (q['nid'], q['chan']), q['nick'].lower())
            self.red.srem('i.%s.chan.%s.ops' % (q['nid'], q['chan']), q['nick'].lower())
        elif q['tag'] == 'MODEC':
            if q['mode'][0] in ['+', '-']:
                self.A.fireEvent('CHANNEL_MODE', modetype=q['mode'][0], **q)
        elif q['tag'] == 'MODEU':
            print q
            nickkey = self.red.get('i.%s.nickkey' % q['nid'])
            if q['mode'][0] in ['+', '-']:
                if 'o' in q['mode']:
                    print 'ye!', nickkey, q['target']
                    if nickkey and nickkey in q['target']:
                        id = int(q['target'][-1])
                        print id
                        if q['mode'][0] == '+':
                            self.red.set('i.%s.worker.%s.%s.op' % (q['nid'], id, q['chan']), 1)
                        else:
                            self.red.set('i.%s.worker.%s.%s.op' % (q['nid'], id, q['chan']), 0)
                        return
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