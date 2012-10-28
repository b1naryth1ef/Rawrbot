from api import Plugin, A
import json, time, random

P = Plugin(A, "Core", 0.1, "B1naryTh1ef")

s_actions = ['slap', 'smite', 'wack', 'pwn', 'rm -rf', 'destroy', 'obliterate', 'refactor', 'git reset --hard']
s_bodyparts = ['tentacle', 'face', 'head', 'dick', 'eye', 'inner thigh']
s_tools = ['gun', 'neek', 'bread', 'black hole', 'stick', 'knife', 'rawrbot', 'python', 'hashtag', 'a.out', 'http://', 'ace']
s_opmsgs = ['Enjoy your +o', 'IMA PUT MY OP IN YOU', 'There you go', '<3', 'Now can we mode +b *!*@* plz?', 'Whose the best bot evar?']

@P.cmd('channels', admin=True)
def cmdChannels(obj):
    obj.pmu('Channels List: (this may take a second)')
    for chan in A.red.smembers('i.%s.chans' % obj.nid):
        numu = A.red.scard('i.%s.chan.%s.users' % (obj.nid, chan))
        numop = A.red.scard('i.%s.chan.%s.ops' % (obj.nid, chan))
        obj.pmu('[#%s] Users: %s | OPs: %s' % (chan, numu, numop))
        time.sleep(1)

@P.cmd('commands', admin=True)
def cmdCommands(obj):
    obj.pmu('Command List: (this may take a second)')
    k = A.commands.keys()
    k.sort()
    for name in k:
        i = A.commands[name]
        obj.pmu('  [%s%s]: %s (%s)' % (A.prefix, name, i['desc'], i['usage']))
        time.sleep(1)

@P.cmd('opme', admin=True, usage='{cmd}')
def cmdOpme(obj):
    if A.red.sismember('i.%s.chan.%s.ops' % (obj.nid, obj.dest.replace('#', '')), obj.nick.lower()):
        return obj.reply('Nice try! You\'re alreay an op!')
    i = A.red.get('i.%s.worker.%s.%s.op' % (obj.nid, obj.id, obj.dest.replace('#', '')))
    if i and int(i):
        obj.raw('MODE %s +o %s' % (obj.dest, obj.nick))
        return obj.reply(random.choice(s_opmsgs))
    return obj.reply('The bot is not an OP so we cant do that! D:')

@P.cmd('maintence', admin=True, usage='{cmd} set={bool}, msg=A spam message', kwargs=True, kbool=['set'], desc="Enable/Disable the bot maintence mode.", alias=['safemode'])
def cmdMaintence(obj):
    if not 'set' in obj.kwargs: return obj.usage()
    A.red.publish('irc.m', json.dumps({'tag':'MAINTENCE', 'mode':obj.kwargs.get('set', False)}))
    if obj.kwargs.get('set'): obj.reply('We are now in maintence mode! Only admins may use commands.')
    else: obj.reply('Maintence mode deactivated! All users may use commands.')
    if obj.kwargs.get('msg'):
        if not obj.kwargs.get('msg').strip(' '): return obj.reply('You cannot send a blank message!')
        for chan in A.red.smembers('i.%s.chans' % obj.nid):
            obj.send(chan, obj.kwargs.get('msg'))
    #@TODO Add global spam option

@P.cmd('config', usage="{cmd} [set/get] key value={bool}", kwargs=True, kbool=['value'], op=True)
def cmdConfig(obj):
    if len(obj.m) < 3: return obj.usage()
    if obj.kwargs.get('value', None) == None: return obj.reply('You must give a value for kwarg "value"')
    v = obj.m[2].strip().lower()
    if v not in A.configs: return obj.reply('Unknown config option %s!')
    k = 'i.%s.chan.%s.cfg.%s' % (obj.nid, obj.dest.replace('#', ''), v)
    if obj.m[1] == 'set':
        A.red.set(k, int(obj.kwargs.get('value')))
        return obj.reply('Set config option "%s" to "%s"' % (v, obj.kwargs.get('value')))
    elif obj.m[1] == 'get':
        return obj.reply('Config option "%s" is set to "%s"' % (v, bool(int(A.red.get(k)))))
    else:
        return obj.reply('Option must be set or get!')

@P.cmd('secret', usage='{cmd}')
def cmdSecret(obj):
    i = A.red.get('i.%s.worker.%s.%s.op' % (obj.nid, obj.id, obj.dest.replace('#', '')))
    if i and int(i):
        return obj.raw('KICK %s %s :%s' % (obj.dest, obj.nick, 'Congrats! You found the secret!'))
    obj.usage()

@P.cmd('join', admin=True, usage="{cmd} <chan>")
def cmdJoin(obj):
    if len(obj.m) < 2: return obj.usage()
    else:
        chan = obj.m[1].replace('#', '').lower()
        if not A.red.sismember('i.%s.chans'% obj.nid, chan):
            A.red.publish('irc.master', json.dumps({'tag':'JOIN', 'chan':chan, 'nid':obj.nid}))
            return obj.reply('Bot has joined channel "#%s"' % chan)
        obj.reply('The bot is already in channel "#%s"!' % chan)

@P.cmd('part', admin=True, usage="{cmd} <chan> [msg]")
def cmdPart(obj):
    if len(obj.m) < 2: return obj.usage()
    else:
        if len(obj.m) > 2: msg = ' '.join(obj.m[2:])
        else: msg = "Bot is leaving..."
        chan = obj.m[1].replace('#', '').lower()
        if A.red.sismember('i.%s.chans' % obj.nid, chan):
            i = {'tag':'PART', 'chan':chan, 'msg':msg, 'nid':obj.nid}
            A.red.publish('irc.master', json.dumps(i))
            return obj.reply('Bot has quit channel "#%s"' % chan)
        obj.reply('Bot is not in channel "#%s' % chan)

@P.cmd('quit', admin=True, kwargs=True, kbool=['confirm'], usage="{cmd} msg=My Message confirm={bool}")
def cmdQuit(obj):
    if not obj.kwargs: return obj.usage()
    if not obj.kwargs.get('confirm'):
        return obj.reply('You must have kwarg confirm true to complete quitting!')
    if not obj.kwargs.get('msg'):
        return obj.reply('You must provide a message to quit!')
    A.red.publish('irc.master', json.dumps({'tag':'QUIT', 'msg':obj.kwargs.get('msg')}))

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

@P.cmd('msg', kwargs=True, kbool=['nick', 'force'], admin=True, 
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

@P.cmd('status', admin=True, usage="{cmd}", desc="Gets info about the bot")
def cmdStatus(obj):
    num_workers = A.red.scard('i.%s.workers' % obj.nid)
    num_masters = A.red.llen('i.masters')
    chans = A.red.smembers('i.%s.chans' % obj.nid)
    num_chans = len(chans)
    num_u, num_t = 0, 0,
    q = []
    for i in chans:
        u = A.red.smembers('i.%s.chan.%s.users' % (obj.nid, i))
        for user in u:
            num_t += 1
            if user.lower() in q: continue
            q.append(user.lower())
            num_u += 1
    del q
    obj.reply('------ STATUS ------')
    obj.reply(' # of Workers: %s' % num_workers)
    obj.reply(' # of Masters: %s' % num_masters)
    obj.reply(' # of Channels: %s' % num_chans)
    obj.reply(' # of Users: %s' % num_t)
    obj.reply(' # of Unique Users: %s' % num_u)
    obj.reply('--------------------')

@P.cmd('addspam', admin=True, kwargs=True,
    usage='{cmd} msg=A spam message duration=(duration in minutes) time=(time between spam (in minutes)) chans=#chana, #chanb (defaults to all)',
    desc="Add a message to be spammed regularly")
def cmdAddspam(obj):
    if not obj.kwargs: return obj.usage()
    if 'msg' not in obj.kwargs or 'time' not in obj.kwargs or 'duration' not in obj.kwargs: return obj.usage()
    obj.sess['time'] = obj.kwargs.get('time')
    obj.sess['duration'] = obj.kwargs.get('duration')
    obj.sess['channels'] = obj.kwargs.get('chans', '')
    obj.sess['chans'] = list(A.red.smembers('i.%s.chans' % obj.nid))
    if obj.sess['channels']:
        obj.sess['chans'] = [i.strip() for i in obj.kwargs.get(obj.sess['channels'], obj.dest).split(',')]
    else: return obj.reply('Incorrect format for kwarg "chans"')
    if not obj.sess['duration'].isdigit() and obj.sess['time'].isdigit():
        return obj.reply('Time and Duration kwargs must be integers (numbers)')
    num = len(A.red.keys('i.p.core.spam.*'))+1
    m = {'msg':obj.kwargs.get('msg'), 'chans':obj.sess['chans'], 'nid':obj.nid}
    A.red.hset('i.p.core.spam.%s' % num, 'data', json.dumps(m))
    A.red.hset('i.p.core.spam.%s' % num, 'time', int(obj.sess['time'])*60)
    A.red.hset('i.p.core.spam.%s' % num, 'last', time.time())
    A.red.hset('i.p.core.spam.%s' % num, 'end', time.time()+(int(obj.sess['duration'])*60))
    A.red.hset('i.p.core.spam.%s' % num, 'active', 1)
    obj.reply('Spam #%s was added!' % num)

@P.cmd('editspam', admin=True, kwargs=True, kbool=['delete', 'active'],
    usage='{cmd} id msg=Edited message duration=New duration time=New time active={bool} delete={bool}',
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
        if obj.kwargs.get('duration')[0] in ['-', '0']: A.red.hset(s, 'end', 0)
        else: A.red.hset(s, 'end', time.time()+(int(obj.kwargs.get('duration')*60)))
    elif 'active' in obj.kwargs:
        A.red.hset(s, 'active', int(obj.kwargs.get('active')))
    elif 'delete' in obj.kwargs:
        A.red.delete(s)
        return obj.reply('Deleted spam #%s!' % obj.m[1])
    A.red.hset(s, 'data', json.dumps(obj.sess['data']))
    obj.reply('Edited spam #%s!' % obj.m[1])    

@P.cmd('viewspams', admin=True, usage='{cmd}', desc="Lists all spams and their details.")
def cmdViewspam(obj):
    for key in A.red.keys('i.p.core.spam.*'):
        msg = json.loads(A.red.hget(key, 'data'))['msg']
        active = A.red.hget(key, 'active')
        obj.reply('#%s - "%s" - Active: %s' % (key.split('.')[-1], msg, bool(active)))

@P.loop(58) #This gets out of sync slowley, do we care that much? Prolly not.
def loopCall():
    for k in A.red.keys('i.p.core.spam.*'):
        if int(A.red.hget(k, 'active')):
            if time.time() > float(A.red.hget(k, 'end')):
                A.red.hset(k, 'active', 0)
                print 'Q1'
                continue
            if (time.time()-float(A.red.hget(k, 'last'))) < float(A.red.hget(k, 'time')): 
                print 'Q2'
                continue
            A.red.hset(k, 'last',   time.time())
            data = json.loads(A.red.hget(k, 'data'))
            for chan in data['chans']:
                _v = A.red.get('i.%s.chan.%s.cfg.spams' % (data['nid'], chan))
                print chan, _v
                if _v and not int(_v): continue
                if A.red.sismember('i.%s.chans' % data['nid'], chan):
                    A.write(data['nid'], chan, data['msg'])
                else: print 'Not in channel %s' % chan #@TODO Fix this
