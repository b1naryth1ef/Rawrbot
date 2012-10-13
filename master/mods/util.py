from api import Cmd, Hook, A
from data import ConfigFile, User, DBModel
from datetime import datetime, timedelta
import time, thread, psutil, os
from peewee import CharField, IntegerField, DateTimeField, BooleanField

__NAME__ = "Util"
__VERSION__ = 0.5
__AUTHOR__ = "B1naryTh1ef"

default_config = {
    'report_channels':['b0tt3st'],
    'ignore_channels':['b0tt3st']
}
config = ConfigFile(name="util", path=['mods', 'config'], default=default_config)

logged_in = [] #(host, time)
LOOPING = False

class AdminMessage(DBModel):
    nick = CharField()
    chan = CharField()
    kind = CharField()
    message = CharField()
    network = IntegerField()
    created = DateTimeField()
    active = BooleanField()
AdminMessage.create_table(True)

def userQ(*args, **kwargs):
    return [i for i in User.select().where(*args, **kwargs)]

def msgQ(*args, **kwargs):
    return [i for i in AdminMessage.select().where(*args, **kwargs)]

def loop():
    while LOOPING:
        time.sleep(60)

def addSpam(msg, duration, interval): pass
def rmvSpam(id): pass

@Cmd('join', admin=True, usage="{cmd} <channel>")
def cmdJoin(obj):
    if len(obj.m) > 1: 
        obj.w.network.addChannel(obj.m[1])
    else: obj.usage()

@Cmd('part', admin=True, kwargs=True, usage="{cmd} <channel> <msg:Part Message>")
def cmdPart(obj):
    if len(obj.m) > 1:
        obj.sess['msg'] = obj.kwargs.get('msg', ' '.join(obj.m[2:]))
        obj.w.network.rmvChannel(obj.m[1], obj.sess['msg'])
    else: obj.usage()

@Cmd('rep', admin=True, usage="{cmd} [list/close/open/rmv/view] [id]")
def cmdReports(obj):
    if len(obj.m) > 1:
        if obj.m[1] == 'list':
            q = msgQ(AdminMessage.kind=="report")
            if not len(q): return obj.reply("No reports!")
            obj.reply('Reports List')
            for i in q:
                if len(i.message) > 50: msg = i.message[:50]+'...'
                else: msg = i.message
                obj.reply('  [%s] #%s -- %s -- "%s"' % ({True:'OPEN', False:'CLOSED'}[i.active], i.id, i.nick, msg))
        elif len(obj.m) < 3:
            obj.usage()
        elif obj.m[1] in ['close', 'open', 'rmv', 'view']:
            if not obj.m[2].isdigit(): obj.reply('ID should be an integer!')
            q = msgQ((AdminMessage.id==int(obj.m[2])) & (AdminMessage.kind=="report"))
            if not len(q): return obj.reply("No results with ID #%s!" % obj.m[2])
            elif len(q) > 1: return obj.reply("Too many results with ID #%s! (Glitch?)" % obj.m[2])
            else: obj.sess['res'] = q[0]

            if obj.m[1] == 'close':
                if obj.sess['res'].active == False: return obj.reply('Report is already closed!')
                obj.sess['res'].active = False
                obj.sess['res'].save()
                obj.reply("Report closed!")    
            elif obj.m[1] == 'open':
                if obj.sess['res'].active == True: return obj.reply("Report is already open!")
                obj.sess['res'].active = True
                obj.sess['res'].save()
            elif obj.m[1] == 'rmv':
                AdminMessage.delete().where((AdminMessage.id==obj.sess['res'].id)).execute()
                obj.reply('Report was deleted!')
            elif obj.m[1] == 'view':
                i = obj.sess['res']
                obj.sess['status'] = {True:'OPEN', False:'CLOSED'}[i.active]
                if i.chan == i.nick:
                    obj.sess['msg'] = "[%s] #%s: %s: %s " % (obj.sess['status'], i.id, i.nick, i.message)
                else:
                    obj.sess['msg'] = "[%s] #%s: [%s] %s: %s [%s]" % (obj.sess['status'], i.id, i.chan, i.nick, i.message)
                obj.reply(obj.sess['msg'])
        else:
            obj.reply('Unknown command %s' % obj.m[1])
    else:
        obj.usage()

#!report msg: msg
@Cmd('report', kwargs=True, usage="{cmd} msg: My report or error message")
def cmdReport(obj):
    if not obj.dest in config.ignore_channels:
        return obj.reply("Reports cannot be sent from this channel!")
    if 'msg' in obj.kwargs.keys():
        obj.sess['msg'] = obj.kwargs['msg']
    elif len(obj.m) > 1:
        obj.sess['msg'] = ' '.join(obj.m[1:])
    else:
        return obj.usage()
    delta = datetime.now()-timedelta(minutes=5)
    q = [i for i in AdminMessage.select().where((AdminMessage.created >= delta))]
    if len(q):
        return obj.reply('You must wait 5 minutes between reports!')
    u = AdminMessage(nick=obj.nick, chan=obj.dest, kind="report", message=obj.sess['msg'], network=obj.w.network.id, 
        created=datetime.now(),
        active=True)
    u.save()
    if len(config.report_channels):
        if obj.pm: obj.sess['msg'] = 'REPORT #%s: %s: %s' % (u.id, u.nick, u.message)
        else: obj.sess['msg'] = 'REPORT #%s: [%s] %s: %s' % (u.id, u.chan, u.nick, u.message)
        for i in config.report_channels:
            if i in obj.w.network.channels.keys():
                obj.send(i, obj.sess['msg'])
    obj.reply('Your message has been reported to the admins and will be reviewed shortly!')

#!status
@Cmd('status', admin=True)
def cmdStatus(obj):
    ps = os.getloadavg()
    pram = psutil.virtual_memory()
    numw = len([i for i in obj.w.network.workers if i != None])
    numc, numu = 0, []
    for chan in obj.w.network.channels.values():
        numc += 1
        for i in chan.users:
            if i.startswith('@') or i.startswith('+'): i = i[1:]
            if i.lower() not in numu:
                numu.append(i.lower())
    numu = len(numu)
    obj.reply('Current RawrBot Status:')
    obj.reply('  # of workers: %s' % numw)
    obj.reply('  # of channels: %s' % numc)
    obj.reply('  # of users: %s' % numu)
    obj.reply('  cpu usage: %s' % str(psutil.cpu_percent())+'%')
    obj.reply('  memory usage: %s' % str(pram.percent)+'%')
    obj.reply('  system load: %.2f %.2f %.2f' % ps)
    obj.reply('End RawrBot Status')

#!reload
@Cmd('reload', admin=True)
def cmdReload(obj):
    if len(obj.m) > 1:
        if A.hasMod(obj.m[1]):
            obj.reply('Reloading %s' % obj.m[1])
            A.reload(obj.m[1])
            obj.reply('Done reloading %s' % obj.m[1])
    obj.reply("Reloading all mods...")
    A.reloadAll(obj=obj, msg="Reloaded!")

@Cmd('leet')
def cmdLeet(obj):
    u = User(
        name=obj.nick.lower(),
        host=obj.host.split('@')[-1].lower(),
        created=datetime.now(),
        locked=False
        )
    u.save()
    A.updateAdmins()
    obj.reply('Your cool now.')

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