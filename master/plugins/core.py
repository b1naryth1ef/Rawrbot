from api import Plugin, A
import json, time

P = Plugin(A, "Core", 0.1, "B1naryTh1ef")

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
    obj.sess['msg'] = obj.kwargs.get('msg', ' '.join(obj.m[1:]))
    obj.sess['chan'] = [i.strip() for i in obj.kwargs.get('chan', obj.dest).split(',')]
    obj.sess['nick'] = obj.kwargs.get('nick', True)
    obj.sess['force'] = obj.kwargs.get('force', False)
    if obj.sess['nick']: obj.sess['msg'] = "%s: %s" % (obj.nick, obj.sess['msg'])
    else: obj.msg = obj.sess['msg']
    if obj.sess['chan'] == ['*']: pass
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
    usage='{cmd} msg=A spam message duration=(duration in minutes) time=(time between spam (in minutes)) chans=+#chanb -#mychan (defaults to all)',
    desc="Add a message to be spammed regularly")
def cmdAddspam(obj):
    if not obj.kwargs: return obj.usage()
    if not 'msg' in obj.kwargs: return obj.usage()
    if not 'time' in obj.kwargs: return obj.usage()
    if not 'duration' in obj.kwargs: return obj.usage()
    obj.sess['msg'] = obj.kwargs.get('msg')
    obj.sess['time'] = obj.kwargs.get('time')
    obj.sess['duration'] = obj.kwargs.get('duration')
    obj.sess['channels'] = obj.kwargs.get('chans', [])
    obj.sess['chans'] = list(A.red.smembers('i.%s.chans' % obj.nid))
    for i in obj.sess['channels']:
        if i.startswith('+'):
            i = i[1:].replace('#', '')
            if i not in obj.sess['chans']:
                obj.sess['chans'].append(i)
        elif i.startswith('-'):
            i = i[1:].replace('#', '')
            if i in obj.sess['chans']:
                obj.sess.remove(i)
        else:
            return obj.reply('Invalid chans format!')
    if not obj.sess['duration'].isdigit() and obj.sess['time'].isdigit():
        return obj.reply('Time and Duration kwargs must be integers (numbers)')
    else:
        obj.sess['duration'] = int(obj.sess['duration'])
        obj.sess['time'] = int(obj.sess['duration'])

    num = A.red.incr('i.p.core.spamid')
    #@TODO Fix this shit
    A.red.hset('i.p.core.spam.%s' % num, 'msg', obj.sess['msg'])
    A.red.hset('i.p.core.spam.%s' % num, 'net', obj.nid)
    A.red.hset('i.p.core.spam.%s' % num, 'time', obj.sess['time'])
    A.red.hset('i.p.core.spam.%s' % num, 'chans', json.dumps(obj.sess['chans']))
    A.red.hset('i.p.core.spam.%s' % num, 'active', True)
    A.red.hset('i.p.core.spam.%s' % num, 'last', time.time())
    A.red.hset('i.p.core.spam.%s' % num, 'end', time.time()+(obj.sess['duration']*60))
    A.red.sadd('i.p.core.spams', num)

    obj.reply('Spam #%s was added!' % num)

_li = 0
@P.loop()
def loopCall():
    print 'Loop!'
    if _li <= 6: 
        _li += 1
        return
    else:
        _li = 0
        for i in A.red.smembers('i.p.core.spams'):
            k = 'i.p.core.spam.%s' % i
            if A.red.hget(k, 'active'):
                if time.time() > A.red.hget(k, 'end'):
                    A.red.hset(k, 'active', False)
                    continue
                if time.time()-A.red.hget(k, 'last') < A.red.hget(k, 'time'): continue
                A.red.hset(k, 'last', time.time())
                nid = A.red.hget(k, 'net')
                msg = A.red.hget(k, 'msg')
                for chan in json.loads(A.red.hget(k, 'chans')):
                    if A.red.sismember('i.%s.chans' % nid, chan):
                        A.write(nid, chan, msg)
                    else:
                        print 'Not in channel %s' % chan #@TODO Fix this
