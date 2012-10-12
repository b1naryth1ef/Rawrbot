from api import Cmd, Hook, A
from data import ConfigFile, User
from datetime import datetime
import time, thread

__NAME__ = "Util"
__VERSION__ = 0.3
__AUTHOR__ = "B1naryTh1ef"

default_config = {}
config = ConfigFile(name="util", path=['mods', 'config'], default=default_config)

logged_in = [] #(host, time)
LOOPING = False

def userQ(**kwargs):
    return [i for i in User.select().where(**kwargs)]

def loop():
    while LOOPING:
        time.sleep(60)

def addSpam(msg, duration, interval): pass
def rmvSpam(id): pass

#!reload
@Cmd('reload', admin=True)
def cmdReload(obj): pass

#!register user
@Cmd('register', admin=True)
def cmdRegister(obj):
    if len(obj.m) >= 2:
        obj.sess['nick'] = obj.m[1]
    else:
        return obj.reply("!register <nick>")
    obj.reply("This may take a moment, please be patient...")
    obj.sess['info'] = obj.w.getUserInfo(obj.sess['nick'])
    if obj.sess['info']:
        if 'auth' in obj.sess['info'].keys():
            if len(userQ(name=obj.sess['nick'].lower())+userQ(host=obj.sess['info']['host'].lower())):
                return obj.reply('This user is already registered!')
            else:
                u = User(
                    name=obj.sess['nick'].lower(), 
                    host=obj.sess['info']['host'].lower(),
                    created=datetime.now(),
                    locked=False)
                u.save()
                A.updateAdmins()
                obj.reply("%s has been registered as an admin!" % obj.sess['nick'].title())
                obj.privmsg(obj.sess['nick'], "You have been registered as an admin! Use your powers wisely!")
        else:
            return obj.reply("This user is not authed on this network. Please ask them to login/register and /mode +x %s" % obj.sess['info']['nick'])
    else:
        obj.reply("The bot could not find info for user %s" % obj.sess['nick'])

#!userlist
@Cmd('userlist', admin=True)
def cmdUserlist(obj):
    obj.privmsg(obj.nick, "User list:")
    for i in userQ():
        obj.privmsg(obj.nick, "  %s: %s@%s" % (i.id, i.name, i.host))
        obj.privmsg(obj.nick, "     Locked: %s" % i.locked)
        obj.privmsg(obj.nick, "     Created: %s" % i.created)
        time.sleep(.1) #So we dont spam
    obj.privmsg(obj.nick, "End user list")

@Cmd('addspam', kwargs=True, admin=True)
def cmdAddspam(obj): pass

@Cmd('rmvspam', kwargs=True, admin=True)
def cmdRmvspam(obj): pass

@Cmd('msg', kwargs=True, kwargsbool=['nick'], admin=True, usage="{cmd} msg:Blah Blah nick:[{bool}] chan:[#achannel]", alias=['m'])
def cmdMsg(obj):
    if len(obj.m) == 1: return obj.usage()
    obj.sess['msg'] = obj.kwargs.get('msg', ' '.join(obj.m[1:]))
    obj.sess['chan'] = obj.kwargs.get('chan', obj.dest).lower()
    obj.sess['nick'] = obj.kwargs.get('nick', True)
    if obj.sess['nick']: obj.sess['msg'] = "%s: %s" % (obj.nick, obj.sess['msg'])
    if not obj.w.network.hasChan(obj.sess['chan']) and obj.sess['chan'] != '*':
        return obj.send(obj.dest, "%s: The bot is not joined too %s" % (obj.nick, obj.sess['chan']))
    else: obj.msg = obj.sess['msg']
    if obj.sess['chan'] == '*': obj.w.network.writeGlobal(obj.msg)
    else: obj.send(obj.sess['chan'], obj.msg)

def onLoad():
    LOOPING = True
    thread.start_new_thread(loop, ())

def onUnload():
    LOOPING = False