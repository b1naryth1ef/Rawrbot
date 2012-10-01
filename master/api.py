import os, sys, time, thread

admins = ['108.174.51.160', "178.79.130.209"]

def Hook(name, chan=None, user=None):
    def deco(func):
        global A
        A.addHook(name, func, chan, user)
        return func
    return deco

def Cmd(name, admin=False):
    def deco(func):
        global A
        A.addCmd(name, func, admin)
        return func
    return deco

class FiredEvent(object):
    def __init__(self, name, **data):
        self.name = name
        if 'data' in data.keys():
            data = data['data']
        self.__dict__.update(data)

    def getDict(self):
        return self.__dict__

class API(object):
    def __init__(self):
        self.prefix = "!"
        self.mods = {}
        self.hooks = {}
        self.commands = {}

    def addCmd(self, name, func, admin=False):
        self.commands[name] = {'admin':admin, 'f':func}

    def parse(self, w, m):
        if m['msg'].startswith(self.prefix):
            c = m['msg'][len(self.prefix):]
            if c in self.commands.keys():
                c = self.commands[c]
                if c['admin'] is True and not m['host'].split('@')[-1] in admins: return
                thread.start_new_thread(c['f'], (FiredEvent(
                    name='cmd',
                    msg=m['msg'],
                    user=m['nick'],
                    dest=m['dest'],
                    m=m['msg'].split(' ')),))
                return True

    def fireHook(self, name, **data):
        if name in self.hooks.keys():
            obj = FiredEvent(name, data=data)
            for i in self.hooks[name]:
                if 'chan' in data and i['c'] != None: 
                    if data['chan'] != i['c']: continue
                if 'user' in data and i['u'] != None: 
                    if data['user'] != i['u']: continue
                thread.start_new_thread(i['f'], (obj,))

    def addHook(self, name, func, chan=None, user=None):
        obj = {'f':func, 'c':chan, 'u':user}
        if name in self.hooks.keys(): self.hooks[name].append(obj)
        else: self.hooks[name] = [obj]

    def rmvHook(self, func):
        for a in self.hooks:
            for b in self.hooks[a]:
                if b['f'] == func:
                    self.hooks[a].pop(self.hooks[a].index(b))

    def loadMods(self):
        print "--Loading mods--"
        for i in os.listdir('mods'):
            if not i.startswith('_') and i.endswith('.py'):
                i = i.split('.py')[0]
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