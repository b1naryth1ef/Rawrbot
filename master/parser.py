import json, thread

class Parser(object):
    def __init__(self, master, red, a):
        self.master = master
        self.red = red
        self.A = a
        self.A.master = master
        self.A.loadPlugins()

        for i in self.red.keys('i.*.user.*.auth'):
            self.red.delete(i)

    def takeMaster(self):
        self.A.canLoop = True
        self.A.loadLoops()

    def rmvUser(self, q):
        for i in self.red.smembers('i.%s.user.%s.chans' % (q['nid'], q['nick'].lower())):
            self.red.srem('i.%s.chan.%s.users' % (q['nid'], i), q['nick'].lower())
            if self.red.sismember('i.%s.chan.%s.ops' % (q['nid'], i), q['nick'].lower()):
                self.red.srem('i.%s.chan.%s.ops' % (q['nid'], i), q['nick'].lower())
        self.red.delete('i.%s.user.%s.chans' % (q['nid'], q['nick'].lower()))
        self.red.delete('i.%s.user.%s.auth' % (q['nid'], q['nick'].lower()))
        self.red.delete('i.%s.user.%s.whoisd' % (q['nid'], q['nick'].lower()))

    def userLeave(self, q):
        self.red.srem('i.%s.chan.%s.users' % (q['nid'], q['chan']), q['nick'].lower())
        self.red.srem('i.%s.chan.%s.ops' % (q['nid'], q['chan']), q['nick'].lower()) #@NOTE We dont care if this works/doesnt
        self.red.srem('i.%s.user.%s.chans' % (q['nid'], q['nick'].lower()), q['chan'])
        if not self.red.scard('i.%s.user.%s.chans' % (q['nid'], q['nick'].lower())):
            self.rmvUser(q)

    def parse(self, q): #@TODO Cleanup this hole fucking thing please
        if 'chan' in q:
            q['chan'] = q['chan'].replace('#', '').lower()
        if q['tag'] == "MSG":
            if q['msg'].startswith(self.A.prefix) and len(q['msg']) > 1 and q['msg'][1] != ' ':
                if self.A.parseCommand(q): return
            self.A.fireEvent('CHANMSG', **q)
        elif q['tag'] == 'NAMES': #@TODO Cleanup
            nickkey = self.red.get('i.%s.nickkey' % q['nid']).lower()
            if nickkey: #@DEV this seems... dangerous?
                for i in q['nicks']:
                    if i[0] == '@':
                        if nickkey in i.lower():
                            id = int(i[-1])
                            self.red.set('i.%s.worker.%s.%s.op' % (q['nid'], id, q['chan']), 1)
                            continue
                        i = i[1:].lower()
                        self.red.sadd('i.%s.chan.%s.ops' % (q['nid'], q['chan']), i)
                    elif i[0] == '+': i = i[1:].lower()
                    elif i[0] in ['&', '~']: i = i[1:].lower()
                    self.red.sadd('i.%s.chan.%s.users' % (q['nid'], q['chan']), i.lower())
                    self.red.sadd('i.%s.user.%s.chans' % (q['nid'], i.lower()), q['chan'])
            else:
                print 'Error parsing NAMES tag. [Namely, nickkey evals false!]'
        elif q['tag'] == 'TOPIC': pass #@TODO track and store this
        elif q['tag'] == 'JOIN':
            nickkey = self.red.get('i.%s.nickkey' % q['nid']).lower()
            if nickkey in q['nick'].lower(): return
            self.red.sadd('i.%s.chan.%s.users' % (q['nid'], q['chan']), q['nick'].lower())
            self.red.sadd('i.%s.user.%s.chans' % (q['nid'], q['nick'].lower()), q['chan'])
            self.A.fireEvent('JOIN', nick=q['nick'].lower(), chan=q['chan'], nid=q['nid'], id=q['id'])
        elif q['tag'] == 'PART': #@TODO Add logic to track when our OWN workers fail (prohax)
            self.userLeave(q)
            self.A.fireEvent('PART', nick=q['nick'].lower(), chan=q['chan'], msg=q['msg'], nid=q['nid'], id=q['id'])
        elif q['tag'] == 'KICK':
            q['kicked'] = q['kicked'].lower()
            q['nick'] = q['nick'].lower()
            if q['us']:
                m = {'tag': 'JOIN', 'chan': q['chan'], 'pw': self.red.get('i.%s.chan.%s.pw' % (q['nid'], q['chan']))}
                self.red.rpush('i.%s.worker.%s' % (q['nid'], q['id']), json.dumps(m))
                return self.A.fireEvent('KICK_W', **q)
            self.userLeave(q)
            self.A.fireEvent('KICK', **q)
        elif q['tag'] == 'MODEC':
            if q['mode'][0] in ['+', '-']:
                self.A.fireEvent('CHANNEL_MODE', modetype=q['mode'][0], **q)
        elif q['tag'] == 'MODEU':
            nickkey = self.red.get('i.%s.nickkey' % q['nid'])
            if q['mode'][0] in ['+', '-']:
                if 'o' in q['mode']:
                    if nickkey and nickkey in q['target']:
                        id = int(q['target'][-1])
                        if q['mode'][0] == '+':
                            self.red.set('i.%s.worker.%s.%s.op' % (q['nid'], id, q['chan']), 1)
                        else:
                            self.red.set('i.%s.worker.%s.%s.op' % (q['nid'], id, q['chan']), 0)
                        return
                    if q['mode'][0] == '-': self.red.srem('i.%s.chan.%s.ops' % (q['nid'], q['chan']), q['target'].lower())
                    else: self.red.sadd('i.%s.chan.%s.ops'% (q['nid'], q['chan']), q['target'].lower())
        elif q['tag'] == 'NICK':
            for i in self.red.smembers('i.%s.user.%s.chans' % (q['nid'], q['nick'].lower())):
                self.red.srem('i.%s.chan.%s.users' % (q['nid'], i), q['nick'].lower())
                self.red.sadd('i.%s.chan.%s.users' % (q['nid'], i), q['newnick'].lower())
                if self.red.sismember('i.%s.chan.%s.ops' % (q['nid'], i), q['nick'].lower()):
                    self.red.srem('i.%s.chan.%s.ops' % (q['nid'], i), q['nick'].lower())
                    self.red.sadd('i.%s.chan.%s.ops' % (q['nid'], i), q['newnick'].lower())
            self.red.sinterstore('i.%s.user.%s.chans' % (q['nid'], q['newnick'].lower()), 'i.%s.user.%s.chans' % (q['nid'], q['nick'].lower()))
            self.red.delete('i.%s.user.%s.chans' % (q['nid'], q['nick'].lower()))
        elif q['tag'] == 'QUIT':
            self.rmvUser(q)
        elif q['tag'] == 'BANNED':
            self.A.fireEvent('BAN_W', **q)
            i = {'tag': 'PART', 'chan': q['chan'], 'msg': 'Bant...', 'nid': q['nid']}
            self.red.publish('irc.master', json.dumps(i))
        elif q['tag'] == 'WHOIS':
            if q.get('nick'):
                print "User %s has been successfully whois'd!" % q.get('nick')
                self.red.set('i.%s.user.%s.whoisd' % (q['nid'], q['nick'].lower()), 1)
                if q.get('auth'):
                    print 'User %s was authed as %s' % (q['nick'], q['auth'])
                    self.red.set('i.%s.user.%s.auth' % (q['nid'], q['nick'].lower()), q['auth'])

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
