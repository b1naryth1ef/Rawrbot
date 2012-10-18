from api import Plugin, A

P = Plugin(A, "Core", 0.1, "B1naryTh1ef")

@P.cmd('msg', kwargs=True, kbool=['nick', 'force'], admin=True, usage="{cmd} msg=A message here! nick[{bool}] chan:[#channels,#by,#comma] force:[{bool}]", alias=['m'])
def cmdMsg(obj):
    print obj.kwargs
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