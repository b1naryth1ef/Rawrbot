import os, sys, time, thread, re

admins = ['108.174.51.160', "178.79.130.209"]

def Hook(name, chan=None, user=None):
    def deco(func):
        global A
        A.addHook(name, func, chan, user)
        return func
    return deco

def Cmd(name, **kwargs):
    def deco(func):
        global A
        A.addCmd(name, func, **kwargs)
        return func
    return deco

class FiredCommand(object):
    def __init__(self, _name=None, _cmd=None, **data):
        self._name = _name
        self._cmd = _cmd
        if 'data' in data.keys():
            data = data['data']
        self.__dict__.update(data)
        self.sess = {}

    def fire(self):
        thread.start_new_thread(self._cmd, (self,))
        return self

    def reply(self, msg):
        if self.pm:
            return self.w.writeUser(self.dest, msg)
        self.w.write(self.dest, '%s: %s' % (self.nick, msg))

    def send(self, dest, msg):
        if self.pm:
            return self.w.writeUser(dest, msg)
        self.w.write(dest, msg)

class FiredEvent(object):
    def __init__(self, api, **data):
        self.api = api
        if 'data' in data.keys():
            data = data['data']
        self.__dict__.update(data)
        self.data = data
        self.sess = {}

    def fire(self):
        for i in self.api.hooks[self._name]:
            if 'chan' in self.data and i['c'] != None: 
                if self.data['chan'] != i['c']: continue
            if 'nick' in self.data and i['u'] != None: 
                if self.data['nick'] != i['u']: continue
            thread.start_new_thread(i['f'], (self,))
        return self

    def getDict(self):
        return self.__dict__

# USE CASES:
# !gtv add Blah >Zoo< 04.08.2012 22:00 CB/NC CTF
# !gtv add Blah >Zoo<
# !gtv set match:1337 a:Blahzy

class API(object):
    def __init__(self):
        self.master = None
        self.red = None
        self.prefix = "!"
        self.mods = {}
        self.hooks = {}
        self.commands = {}

    def addCmd(self, name, func, admin=False, kwargs=False, kwargsbool=[]):
        self.commands[name] = {'admin':admin, 'f':func, 'kwargs':kwargs, 'kbool':kwargsbool}

    def parse(self, w, m):
        if m['msg'].startswith(self.prefix):
            m['m'] = m['msg'].split(' ')
            m['kwargs'] = {}
            if m['m'][0][len(self.prefix):] in self.commands.keys():
                c = self.commands[m['m'][0][len(self.prefix):]]
                if m['nick'] == m['dest']: m['pm'] = True
                else: m['pm'] = False
                if c['admin'] is True and not m['host'].split('@')[-1] in admins: 
                    return
                if c['kwargs']:
                    m['kwargs'] = dict(re.findall(r'([^: ]+):([^ ]+)?', ' '.join(m['m'][1:])))
                    for i in m['kwargs']:
                        if i not in c['kbool']: continue
                        val = m['kwargs'][i]
                        if val.isdigit() and int(val) in [0, 1]:
                            m['kwargs'][i] = bool(int(val))
                        elif val.lower() in ['y', 'n', 'true', 'false']:
                            m['kwargs'][i] = {'y':True, 'n':False, 'true':True, 'false':False}[val.lower()]
                        else: 
                            if m['pm']: return w.writeUser(m['nick'], '%s: The kwarg "%s" must be 1/0, Y/N or True/False!' % (m['nick'], i))
                            else: return w.write(m['dest'], '%s: The kwarg "%s" must be 1/0, Y/N or True/False!'  % (m['nick'], i))
                m['_name'] = 'cmd'
                m['_cmd'] = c['f'] 
                m['w'] = w
                FiredCommand(**m).fire()
                return True

    def fireHook(self, name, **data):
        if name in self.hooks.keys():
            data['_name'] = name
            FiredEvent(self, **data).fire()
            
    def addHook(self, name, func, chan=None, user=None):
        obj = {'f':func, 'c':chan, 'u':user}
        if name in self.hooks.keys(): self.hooks[name].append(obj)
        else: self.hooks[name] = [obj]

    def rmvHook(self, func):
        for a in self.hooks:
            for b in self.hooks[a]:
                if b['f'] == func:
                    self.hooks[a].pop(self.hooks[a].index(b))

    def loadMods(self, plugins=[]):
        print "--Loading mods--"
        for i in os.listdir('mods'):
            if not i.startswith('_') and i.endswith('.py'):
                i = i.split('.py')[0]
                if plugins and i not in plugins: continue
                __import__('mods.%s' % i)
                self.load(i)
        print "--DONE--"      

    def load(self, i):
        mod = sys.modules['mods.%s' % i]
        self.mods[i] = mod
        if hasattr(mod, "onLoad"): mod.onLoad()
        print "Loaded %s v%s by %s" % (mod.__NAME__, mod.__VERSION__, mod.__AUTHOR__ )

    def reloadall(self):
        for i in self.mods.keys():
            self.reload(i)
            
    def reload(self, i):
        if hasattr(self.mods[i], "onUnload"): self.mods[i].onUnload()
        self.mods[i] = reload(self.mods[i])
        if hasattr(self.mods[i], "onLoad"): self.mods[i].onLoad()

    def unload(self, i):
        if hasattr(self.mods[i], "onUnload"): self.mods[i].onUnload()
        del sys.modules['mods.%s' % i]

A = API()