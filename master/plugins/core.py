# -*- coding: utf-8 -*-
from api import Plugin, A
import json, time, random, os

P = Plugin(A, "Core", 0.2, "B1naryTh1ef")

s_actions = ['slap', 'smite', 'wack', 'pwn', 'rm -rf', 'destroy', 'obliterate', 'refactor', 'git reset --hard']
s_bodyparts = ['tentacle', 'face', 'head', 'dick', 'eye', 'inner thigh']
s_tools = ['gun', 'neek', 'bread', 'black hole', 'stick', 'knife', 'rawrbot', 'python', 'hashtag', 'a.out', 'http://']
s_opmsgs = ['Enjoy your +o', 'IMA PUT MY OP IN YOU', 'There you go', '<3', 'Now can we mode +b *!*@* plz?', 'Whose the best bot evar?']

@P.cmd('addadmin', usage="{cmd} name chan=#mychan", gadmin=True, kwargs=True)
def addAdmin(obj):
    if len(obj.m) < 2: return obj.usage()
    if obj.kwargs.get('chan'):
        s = 'i.%s.chan.%s.admins' % (obj.nid, obj.kwargs.get('chan'))
    else:
        s = 'i.%s.admins' % obj.nid
    if A.red.sismember(s, obj.m[1].lower()):
        return obj.reply('That user is already an admin!')
    else:
        A.red.sadd(s, obj.m[1].lower())
        if obj.kwargs.get('chan'):
            obj.reply('Added %s as a admin for %s!' % (obj.m[1], obj.kwargs.get('chan')))
        else:
            obj.reply('Added %s as a global admin!' % obj.m[1])

@P.cmd('rmvadmin', usage="{cmd} name chan=#mychan", gadmin=True, kwargs=True)
def rmvAdmin(obj):
    if len(obj.m) < 2: obj.usage()
    if obj.kwargs.get('chan'): s = 'i.%s.chan.%s.admins' % (obj.nid, obj.kwargs.get('chan'))
    else: s = 'i.%s.admins' % obj.nid
    if A.red.sismember(s, obj.m[1].lower()):
        A.red.srem(s, obj.m[1].lower())
        return obj.reply('Removed %s as an admin!' % obj.m[1].lower())
    else:
        return obj.reply('User %s is not an admin!' % obj.m[1].lower())

@P.cmd('source')
def cmdSource(obj):
    obj.smu("\x033RawrBot Source Code\x03: hhttps://github.com/b1naryth1ef/Rawrbot")

@P.cmd("hoot")
def cmdHoot(obj):
    owl_strings = ['YOLO', 'g1nk0 doesn\'t life (c) anderson']
    obj.smu('\x036H00t H00t Motherfucker, #owl-team swag!\x03 [\x035%s\x03]' % random.choice(owl_strings))

@P.cmd('derp', nolist=True)
def cmdDerp(obj):
    if len(obj.m) < 2: return
    if obj.m[1] == 'neek': return obj.reply("Sorry, I'm too drunk to respond right now, please contact me by buying booze and placing it outside my condo door.")
    elif obj.m[1] == 'tony': return obj.reply('Hit. HIT. HIT HIT HIT HIT. Stay. HIT. HIT MOTHERFUCKER. Hit. Stay? Hit. Hit mystery. Hit trippy.')
    elif obj.m[1] == 'ictere': return obj.reply("The laws of physics make your statement incorrect.")
    elif obj.m[1] == 'scuba': return obj.reply('ROBOTS!')
    elif obj.m[1] == 'b1n': return obj.reply('B1N IS AMAZING AND WONDERFUL AND DIDNT WRITE THIS AND OMG HE\'S SO GREAT LIKE RLLY!')
    elif obj.m[1] == 'b00bs': return obj.reply("B00bs clan, ruining UrT and banning innocents since forever.")

@P.cmd('update', desc="Update the bot from git", gadmin=True)
def cmdUpdate(obj):
    obj.reply('Searching for updates on the git repo...')
    l = os.popen('git pull origin dev').readlines()
    if 'Already up-to-date.\n' in l:
        return obj.reply("No updates availible from git!")
    A.red.set("i.maintmode", int(1))
    obj.reply("An update was found on the git repo!")
    obj.reply('Updating and reloading...')
    A.reloadPlugins(obj.reply, 'Update complete!')
    A.red.set("i.maintmode", int(0))

@P.cmd('channels', gadmin=True)
def cmdChannels(obj):
    obj.pmu('Channels List: (this may take a second)')
    for chan in A.red.smembers('i.%s.chans' % obj.nid):
        numu = A.red.scard('i.%s.chan.%s.users' % (obj.nid, chan))
        numop = A.red.scard('i.%s.chan.%s.ops' % (obj.nid, chan))
        obj.pmu('[#%s] Users: %s | OPs: %s' % (chan, numu, numop))
        A.throttle()

@P.cmd('commands', gadmin=True)
def cmdCommands(obj):
    obj.pmu('Command List: (this may take a second)')
    k = A.commands.keys()
    k.sort()
    for name in k:
        i = A.commands[name]
        if i['nolist']: continue
        obj.pmu('  [%s%s]: %s' % (A.prefix, name, i['desc']))
        A.throttle()

@P.cmd('opme', admin=True, usage='{cmd}')
def cmdOpme(obj):
    if A.red.sismember('i.%s.chan.%s.ops' % (obj.nid, obj.dest.replace('#', '')), obj.nick.lower()):
        return obj.reply('Nice try! You\'re alreay an op!')
    i = A.red.get('i.%s.worker.%s.%s.op' % (obj.nid, obj.id, obj.dest.replace('#', '')))
    if i and int(i):
        obj.raw('MODE %s +o %s' % (obj.dest, obj.nick))
        return obj.reply(random.choice(s_opmsgs))
    return obj.reply('The bot is not an OP so we cant do that! D:')

@P.cmd('maintence', gadmin=True, usage='{cmd} set={bool}, msg=A spam message', kwargs=True, kbool=['set'], desc="Enable/Disable the bot maintence mode.", alias=['safemode'])
def cmdMaintence(obj):
    if not 'set' in obj.kwargs: return obj.usage()
    A.red.set("i.maintmode", int(obj.kwargs.get('set', False)))
    if obj.kwargs.get('set'): obj.reply('We are now in maintence mode! Only admins may use commands.')
    else: obj.reply('Maintence mode deactivated! All users may use commands.')
    if obj.kwargs.get('msg'):
        if not obj.kwargs.get('msg').strip(' '): return obj.reply('You cannot send a blank message!')
        for chan in A.red.smembers('i.%s.chans' % obj.nid):
            obj.send(chan, obj.kwargs.get('msg'))

@P.cmd('config', usage="{cmd} [set/get] key value={bool}", gadmin=True, kwargs=True, kbool=['value'], always=True)
def cmdConfig(obj):
    #if not obj.op and not obj.admin: return obj.reply("You must be an admin or op to set channel config values!")
    if len(obj.m) < 3: return obj.usage()
    if obj.kwargs.get('value', None) is None and obj.m[1] != 'get': return obj.reply('You must give a value for kwarg "value"')
    v = obj.m[2].strip().lower()
    if v not in A.configs: return obj.reply('Unknown config option %s!' % v)
    k = 'i.%s.chan.%s.cfg.%s' % (obj.nid, obj.dest.replace('#', ''), v)
    if obj.m[1] == 'set':
        A.red.set(k, int(obj.kwargs.get('value')))
        return obj.reply('Set config option "%s" to "%s"' % (v, obj.kwargs.get('value')))
    elif obj.m[1] == 'get':
        return obj.reply('Config option "%s" is set to "%s"' % (v, bool(int(A.red.get(k)))))
    else:
        return obj.reply('Option must be set or get!')

@P.cmd('secret', usage='{cmd}', nolist=True)
def cmdSecret(obj):
    if obj.isBotOp():
        return obj.raw('KICK %s %s :%s' % (obj.dest, obj.nick, 'Congrats! You found the secret!'))
    obj.reply('I DONT KNOW WHAT YOUR TALKING ABOUT!')

@P.cmd('join', gadmin=True, usage="{cmd} <chan> [pw]")
def cmdJoin(obj):
    if len(obj.m) < 2: return obj.usage()
    else:
        pw = ''
        if len(obj.m) > 3:
            pw = obj.m[2]
        chan = obj.m[1].replace('#', '').lower()
        if not A.red.sismember('i.%s.chans'% obj.nid, chan):
            A.red.publish('irc.master', json.dumps({'tag': 'JOIN', 'chan': chan, 'nid': obj.nid, 'pw': pw}))
            return obj.reply('Bot has joined channel "#%s"' % chan)
        obj.reply('The bot is already in channel "#%s"!' % chan)

@P.cmd('part', gadmin=True, usage="{cmd} <chan> [msg]")
def cmdPart(obj):
    if len(obj.m) < 2: return obj.usage()
    else:
        if len(obj.m) > 2: msg = ' '.join(obj.m[2:])
        else: msg = "Bot is leaving..."
        chan = obj.m[1].replace('#', '').lower()
        if A.red.sismember('i.%s.chans' % obj.nid, chan):
            i = {'tag': 'PART', 'chan': chan, 'msg': msg, 'nid': obj.nid}
            A.red.publish('irc.master', json.dumps(i))
            return obj.reply('Bot has quit channel "#%s"' % chan)
        obj.reply('Bot is not in channel "#%s' % chan)

@P.cmd('quit', gadmin=True, kwargs=True, kbool=['confirm'], usage="{cmd} msg=My Message confirm={bool}")
def cmdQuit(obj):
    if not obj.kwargs: return obj.usage()
    if not obj.kwargs.get('confirm'):
        return obj.reply('You must have kwarg confirm true to complete quitting!')
    if not obj.kwargs.get('msg'):
        return obj.reply('You must provide a message to quit!')
    A.red.publish('irc.master', json.dumps({'tag': 'QUIT', 'msg': obj.kwargs.get('msg')}))

@P.cmd('slap', admin=True, usage="{cmd} <user>")
def cmdSlap(obj):
    act = random.choice(s_actions)
    bp = random.choice(s_bodyparts)
    tool = random.choice(s_tools)
    if len(obj.m) < 2: return obj.usage()
    m = "%s %s's %s across the %s with a %s." % (obj.nick, act, obj.m[1], bp, tool)
    obj.smu(m)

@P.cmd('help')
def cmdHelp(obj):
    obj.pmu('To avoid spamming, we wont list commands. For commands goto http://fixthislater.com.')
    obj.pmu('If you need to report a problem with the bot, or want help from a real person, please use !report.')

@P.cmd('reload')
def cmdReload(obj):
    obj.reply('Reloading plugins...')
    A.reloadPlugins(obj.reply, 'Reloaded all plugins!')

@P.cmd('msg', kwargs=True, kbool=['nick', 'force'], gadmin=True,
    usage="{cmd} msg=A message here! nick=[{bool}] chan=[#channels,#by,#comma] force=[{bool}]",
    alias=['m'],
    desc="Send a message from the bot")
def cmdMsg(obj):
    if len(obj.m) == 1: return obj.usage()
    if not 'msg' in obj.kwargs: return obj.reply('You must specify a message to send!')
    obj.sess['msg'] = obj.kwargs.get('msg', '')
    obj.sess['chan'] = [i.strip() for i in obj.kwargs.get('chan', obj.dest).split(',')]
    obj.sess['nick'] = obj.kwargs.get('nick', True)
    obj.sess['force'] = obj.kwargs.get('force', False)
    if not obj.sess['msg'].strip(' '): return obj.reply('You cannot send an empty message!')
    if obj.sess['nick']: obj.sess['msg'] = "%s: %s" % (obj.nick, obj.sess['msg'])
    else: obj.msg = obj.sess['msg']
    if obj.sess['chan'] == ['*']: pass #@TODO do this
    elif obj.sess['chan']:
        fails = []
        for i in obj.sess['chan']:
            i = i.replace('#', '')
            if A.validChan(obj.nid, i): obj.send(i, obj.sess['msg'])
            elif obj.sess['force']: pass
            else: fails.append(i)
        if len(fails):
            obj.reply('Failed sending to the following channels: %s' % ', '.join(fails))

@P.cmd('status', gadmin=True, usage="{cmd}", desc="Gets info about the bot")
def cmdStatus(obj): #@TODO Update
    A.red.delete('i.temp.res')
    num_workers = A.red.scard('i.%s.workers' % obj.nid)
    num_work_total = 0
    for key in A.red.keys('i.*.workers'):
        num_work_total += A.red.scard(key)
    num_masters = A.red.llen('i.masters')
    num_chans, num_useru, num_usert = 0, 0, 0
    for chan in A.red.smembers('i.%s.chans' % obj.nid):
        num_chans += 1
        num_usert += A.red.scard('i.%s.chan.%s.users' % (obj.nid, chan))
        A.red.sunionstore('i.temp.res', 'i.%s.chan.%s.users' % (obj.nid, chan), 'i.temp.res')
    num_useru = A.red.scard('i.temp.res')
    obj.reply('------ STATUS ------')
    obj.reply("Workers: %s (%s total) | Masters: %s" % (num_workers, num_work_total, num_masters))
    obj.reply("Users: %s | Unique: %s | Channels: %s" % (num_usert, num_useru, num_chans))

@P.cmd('winfo', gadmin=True, usage="{cmd} <wid>", desc="Get info about an single worker")
def cmdWinfo(obj):
    if not len(obj.m) > 1: return obj.usage()
    if not obj.m[1].isdigit(): return obj.reply("Worker ID must be an integer!")
    if not A.red.sismember('i.%s.workers' % obj.nid, int(obj.m[1])): return obj.reply("No worker with ID #%s!" % obj.m[1])
    w_chans, w_users = 0, 0
    for chan in A.red.smembers('i.%s.worker.%s.chans' % (obj.nid, obj.m[1])):
        w_chans += 1
        w_users += A.red.scard('i.%s.chan.%s.users' % (obj.nid, chan))
    w_uptime = time.time()-float(A.red.get('i.%s.worker.%s.uptime' % (obj.nid, obj.m[1])))
    return obj.reply("Worker #%s: %s channels, %s users, %s uptime" % (obj.m[1], w_chans, w_users, w_uptime))

@P.cmd('addspam', admin=True, kwargs=True, kbool=['spam'],
    usage='{cmd} msg=A spam message duration=(duration in minutes) time=(time between spam (in minutes)) chans=#chana, #chanb (defaults to all) spam={bool}',
    desc="Add a message to be spammed regularly")
def cmdAddspam(obj):
    if not obj.kwargs: return obj.usage()
    if 'msg' not in obj.kwargs or 'time' not in obj.kwargs or 'duration' not in obj.kwargs: return obj.usage()
    obj.sess['time'] = obj.kwargs.get('time')
    obj.sess['duration'] = obj.kwargs.get('duration')
    obj.sess['channels'] = obj.kwargs.get('chans', '')
    obj.sess['chans'] = list(A.red.smembers('i.%s.chans' % obj.nid))
    if obj.sess['channels']:
        obj.sess['chans'] = [i.strip().replace('#', '') for i in obj.sess['channels'].split(',')]
    else: return obj.reply('Incorrect format for kwarg "chans"')
    if not obj.sess['duration'].isdigit() and obj.sess['time'].isdigit():
        return obj.reply('Time and Duration kwargs must be integers (numbers)')
    num = A.callHook('core_spam_add', obj.nid, obj.kwargs.get('msg'), obj.sess['chans'], int(obj.kwargs.get('duration')), int(obj.kwargs.get('time')))
    obj.reply('Spam #%s was added!' % num)
    if obj.kwargs.get('spam'): A.callHook('core_spam_push', num)

@P.cmd('editspam', admin=True, kwargs=True, kbool=['delete', 'active', 'spam'],
    usage='{cmd} id msg=Edited message duration=New duration time=New time active={bool} delete={bool}, spam={bool}',
    desc="Edit a spam message, you *cannot* edit the channels of a spam!")
def cmdEditspam(obj):
    if not obj.kwargs: return obj.usage()
    if not obj.m[1].isdigit(): return obj.reply('That is an invalid ID #!')
    if 'i.p.core.spam.%s' % int(obj.m[1]) not in A.red.keys('i.p.core.spam.*'): return obj.reply('No spam with that ID #!')
    s = 'i.p.core.spam.%s' % int(obj.m[1])
    obj.sess['data'] = json.loads(A.red.hget(s, 'data'))
    if 'msg' in obj.kwargs: obj.sess['data']['msg'] = obj.kwargs.get('msg')
    elif 'time' in obj.kwargs:
        if not obj.kwargs.get('time').isdigit(): return obj.reply('Time kwarg must be integer (number)!')
        print 'Time == %s' % str(int(obj.kwargs.get('time'))*60)
        A.red.hset(s, 'time', int(obj.kwargs.get('time'))*60)
    elif 'duration' in obj.kwargs:
        if not obj.kwargs.get('time').isdigit(): return obj.reply('Duration kwarg must be integer (number)!')
        if obj.kwargs.get('duration')[0] in ['-']: A.red.hset(s, 'end', 0)
        else: A.red.hset(s, 'end', time.time()+(int(obj.kwargs.get('duration')*60)))
    elif 'active' in obj.kwargs:
        A.red.hset(s, 'active', int(obj.kwargs.get('active')))
    elif 'delete' in obj.kwargs:
        A.red.delete(s)
        return obj.reply('Deleted spam #%s!' % obj.m[1])
    if 'spam' in obj.kwargs:
        A.callHook('core_spam_push', int(obj.m[1]))
    A.red.hset(s, 'data', json.dumps(obj.sess['data']))
    obj.reply('Edited spam #%s!' % obj.m[1])

@P.cmd('spams', admin=True, usage='{cmd}', desc="Lists all spams and their details.")
def cmdViewspam(obj):
    for key in A.red.keys('i.p.core.spam.*'):
        msg = json.loads(A.red.hget(key, 'data'))['msg']
        active = A.red.hget(key, 'active')
        obj.reply('#%s - "%s" - Active: %s' % (key.split('.')[-1], msg, bool(active)))

@P.apih('core_spam_add')
def coreSpamAdd(nid, msg, chans, duration, timex, active=1):
    num = len(A.red.keys('i.p.core.spam.*'))+1
    m = {'msg': msg.replace('\\', ''), 'chans': chans, 'nid': nid}
    A.red.hset('i.p.core.spam.%s' % num, 'data', json.dumps(m))
    A.red.hset('i.p.core.spam.%s' % num, 'time', timex*60)
    A.red.hset('i.p.core.spam.%s' % num, 'last', time.time())
    A.red.hset('i.p.core.spam.%s' % num, 'end', time.time()+(duration*60))
    A.red.hset('i.p.core.spam.%s' % num, 'active', active)
    return num

@P.apih('core_spam_push')
def coreSpamPush(id, update_time=True):
    print 'Pushing %s' % id
    k = 'i.p.core.spam.%s' % id
    if update_time: A.red.hset(k, 'last',   time.time())
    try: data = json.loads(A.red.hget(k, 'data'))
    except:
        print 'Failed to push spam "%s"!' % id
        return
    for chan in data['chans']:
        _v = A.red.get('i.%s.chan.%s.cfg.spams' % (data['nid'], chan))
        if _v and not int(_v): continue
        if A.red.sismember('i.%s.chans' % data['nid'], chan):
            A.write(data['nid'], chan, data['msg'])
        else: print 'Not in channel %s' % chan #@TODO Fix this

@P.loop(55) #This gets out of sync slowley, do we care that much? Prolly not.
def loopCall():
    for k in A.red.keys('i.p.core.spam.*'):
        if A.red.hget(k, 'active').isdigit() and float(A.red.hget(k, 'active')):
            if float(A.red.hget(k, 'end')) != -1 and time.time() > float(A.red.hget(k, 'end')):
                A.red.hset(k, 'active', 0)
                continue
            if float(time.time()-float(A.red.hget(k, 'last'))) < float(A.red.hget(k, 'time')):
                continue
            A.callHook('core_spam_push', float(k.split('.')[-1]))
