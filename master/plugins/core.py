from api import Plugin, A

P = Plugin(A, "Core", 0.1, "B1naryTh1ef")

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
    num_masters = A.red.zcard('i.masters')
    chans = A.red.smembers('i.%s.chans' % obj.nid)
    num_chans = len(chans)

    num_ops, num_voice, num_u, num_t = 0, 0, 0, 0
    q = []
    print chans
    for i in chans:
        print i
        u = A.red.zrangebyscore('i.%s.chan.%s.users' % (obj.nid, i), 0, 1, withscores=True)
        for user, code in u:
            print user, code, i
            num_t += 1
            if code == 1: num_voice += 1
            elif code == 2: num_ops += 1
            if user.lower() in q: continue
            q.append(user.lower())
            num_u += 1
    del q
    
    obj.reply('------ STATUS ------')
    obj.reply('  # of Workers: %s' % num_workers)
    obj.reply('  # of Masters: %s' % num_masters)
    obj.reply('  # of Channels: %s' % num_chans)
    obj.reply('  USER INFO:')
    obj.reply('    # of Users: %s' % num_t)
    obj.reply('    # of Unique Users: %s' % num_u)
    obj.reply('    # of Ops: %s' % num_ops)
    obj.reply('    # of Voices: %s' % num_voice)
    obj.reply('--------------------')