import re, thread, json
import sys, os, time
import random, __builtin__

class FiredEvent():
    def __init__(self, api, name, data={}):
        self._name = name
        self._data = data
        self._api = api
        self.sess = {}
        self.__dict__.update(data)

class FiredCommand(FiredEvent):
    def reply(self, msg):
        if self.pm: self.privmsg(self.nick, msg)
        else: self.send(self.dest, '%s: %s' % (self.nick, msg))

    def usage(self):
        i = self._cmd['usage'].format(**{'cmd':self._name, 'bool':'true/false|on/off|1/0'})
        self.reply(self._prefix+i)

    def privmsg(self, user, msg):
        k = {'tag':'PM', 'msg':msg, 'nick':user}
        self._api.red.rpush('i.%s.worker.%s' % (self.nid, self.id), json.dumps(k))

    def send(self, chan, msg): #@TODO Check if valid channel?
        k = {'tag':'MSG', 'chan':chan.replace('#', ''), 'msg':msg}
        self._api.red.rpush('i.%s.chan.%s' % (self.nid, k['chan']), json.dumps(k))

class Plugin():
    def __init__(self, api, name="NullPlugin", version=0.1, author="Null"):
        self.api = api
        self.realname = name.lower().replace(' ', '')
        self.mod = None
        self.name = name
        self.version = version
        self.author = author

        self.cmds = []
        self.hooks = []

        self.api.plugins[self.realname] = self

    def loaded(self):
        print self.api.mods[self.realname]
        self.mod = self.api.mods[self.realname]

    def loop(self):
        def deco(func):
            self.api.loops.append(func)
            return func
        return deco

    def cmd(self, name, **kwargs): #@TYPE Decorator
        def deco(func):
            self.api.addCommand(self, name, func, **kwargs)
            self.cmds.append(name)
            return func
        return deco

    def hook(self, name): #@TYPE Decorator
        def hook(func):
            func.id = self.api.addHook(self, name, func)
            self.hooks.append(func.id)
            return func
        return deco

    def reload(self):
        self.unload()
        self.mod = reload(self.mod)
        self.mod.plugin = self
        if hasattr(self.mod, 'onLoad'): self.onLoad()

    def unload(self):
        if hasattr(self.mod, 'onUnload'): self.onUnload()
        for i in self.cmds:
            self.api.rmvCommand(i)
        for i in self.hooks:
            self.api.rmvHook(i)

class API(object):
    def __init__(self, red):
        self.red = red
        self.prefix = "!"

        self.mods = {}
        self.plugins = {}
        self.commands = {}
        self.alias = {}
        self.hook_key = {}
        self.hooks = {}
        self.loops = []

        thread.start_new_thread(self.loop, ())

    def loop(self):
        while True:
            for i in self.loops:
                i()
            time.sleep(10)

    def validChan(self, net, chan):
        return self.red.sismember('i.%s.chans' % net, chan)

    def write(self, net, chan, msg):
        msg = {
            'tag':'MSG',
            'chan':chan.replace('#', ''),
            'msg':msg}
        self.red.rpush('i.%s.chan.%s' % (net, msg['chan']), json.dumps(msg))

    def writeUser(self, m, user, msg):
        msg = {
            'tag':'PM',
            'nick':user,
            'msg':msg}
        self.red.rpush('i.%s.worker.%s' % (m['nid'], m['id']), json.dumps(msg))

    def isAdmin(self, net, host): 
        host = host.split('@')[-1].strip()
        return self.red.sismember('i.%s.admins' % (net), host)

    def parseCommand(self, data):
        m = data['msg'].split(' ')
        obj = FiredCommand(self, m[0][len(self.prefix):], data)
        obj.m = m
        obj._prefix = self.prefix
        obj._cmd = self.getCommand(obj._name)
        if data['nick'] == data['dest']: obj.pm = True
        else: obj.pm = False
        if obj._cmd:
            if obj._cmd['admin'] is True and not self.isAdmin(data['nid'], data['host']):
                msg = "You must be an admin to use that command!"
                if obj.pm: self.writeUser(data, data['nick'], msg)
                else: self.write(data['nid'], data['dest'], '%s: %s' % (data['nick'], msg))
                return
            if obj._cmd['kwargs']:
                obj.kwargs = dict(re.findall(r'([^ \=]+)\=[ ]*(.+?)?(?:(?= [^ \\]+\=)|$)', ' '.join(m[1:])))
                for i in obj._cmd['kbool']:
                    if i in obj.kwargs:
                        kb = obj.kwargs[i]
                        if kb.isdigit() and int(kb) in [0, 1]: 
                            obj.kwargs[i] = bool(int(kb))
                        elif kb.lower() in ['y', 'n', 'true', 'false', 'on', 'off']:
                            obj.kwargs[i] = {'y':True, 'n':False, 'true':True, 'false':False, 'on':True, 'off':False}[kb.lower()]
                        else:
                            msg = 'Kwarg %s must be y/n, true/false, on/off 1/0!' % i
                            if obj.pm: self.writeUser(data, data['nick'], msg)
                            else: self.write(data['nid'], data['dest'], '%s: %s' % (data['nick'], msg))
                            return
            thread.start_new_thread(obj._cmd['f'], (obj,))
            return True
        else:
            last = self.red.get('i.%s.lastsenterr.%s' % (data['nid'], data['nick'].lower()))
            if last and time.time()-last < 5: return #Prevent spamming
            msg = 'No such command "%s"!' % obj._name
            if obj.pm: self.writeUser(data, data['nick'], msg)
            else: self.write(data['nid'], data['dest'], '%s: %s' % (data['nick'], msg))
            self.red.set('i.%s.lastsenterr.%s' % (data['nid'], data['nick'].lower()), time.time())
            self.red.expire('i.%s.lastsenterr.%s' % (data['nid'], data['nick'].lower()), 30)

    def addCommand(self, plugin, name, func, admin=False, kwargs=False, kbool=[], usage="", alias=[], desc=""):
        if name in self.commands.keys(): raise Exception('Command with name %s already exists!' % name)
        self.commands[name] = {
            'plug':plugin,
            'f':func,
            'admin':admin,
            'kwargs':kwargs,
            'kbool':kbool,
            'usage':usage,
            'alias':alias,
            'desc':desc,
        }

        for i in alias:
            self.alias[i] = name

    def rmvCommand(self, name):
        if name in self.commands.keys():
            del self.commands[name]

    def getCommand(self, name):
        if name in self.commands.keys():
            return self.commands[name]
        elif name in self.alias.keys():
            return self.commands[self.alias[name]]

    def fireEvent(self, name, data):
        if name.upper() in self.hooks:
            obj = FiredEvent(self, name.upper(), data)
            for i in self.hooks[name]:
                thread.start_new_thread(self.hook_key[i], obj)

    def addHook(self, plugin, hook, func):
        id = random.randint(1111111, 9999999)
        if id in self.hook_key.keys(): return addHook(plugin, hook, func) #Recursion fix for edgecase
        self.hook_key[id] = (plugin, hook, func)
        if hook in self.hooks.keys(): self.hooks[hook].append(id)
        else: self.hooks[hook] = [id]
        return id

    def rmvHook(self, hid):
        i = self.hook_key[hid]
        self.hooks[i[1]].remove(hid)
        del self.hook_key[hid]

    def loadPlugins(self):
        for i in os.listdir('plugins'):
            if not i[0] in ['.', '_'] and i.endswith('.py'):
                i = i.split('.py')[0]
                if self.hasPlugin(i): continue
                __import__('plugins.%s' % i, globals(), locals(), [], -1)
                self.loadPlugin(i)

    def hasPlugin(self, name):
        if name in self.plugins.keys():
            return True
        return False

    def loadPlugin(self, f):
        self.mods[f] = sys.modules['plugins.%s' % f]
        if hasattr(f, 'onBoot'): mod.onBoot()
        if 'f' in self.plugins:
            self.plugins[f].loaded()

    def reloadPlugins(self, call=None, *args, **kwargs):
        for plugin in self.plugins.values():
            plugin.reload()
        if call:
            call(*args, **kwargs)

A = None
