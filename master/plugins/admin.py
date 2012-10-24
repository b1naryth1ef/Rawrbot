from api import Plugin, A
from data import ConfigFile

P = Plugin(A, "Admin", 0.1, "B1naryTh1ef")

default_cfg = {
    'admin_chans':['b1naryth1ef', 'rawrbot.admins']
}

cfg = ConfigFile(name='admin', path=['plugins', 'config'], default=default_cfg)

@P.cmd('report', usage='{cmd} My message to admins', 
    desc="Send a message to the admins (IN ENGLISH), or ask for assistance. (Abuse results in banz!)")
def cmdReport(obj):
    if len(obj.m) < 2:
        return obj.reply('Please specify a message to describe the problem your having (in english)!')
    if not obj.admin and A.red.get('i.p.core.repu.%s' % obj.nick): #This isnt horribly secure, but w/e
        return obj.reply('Please wait 10 minutes in between sending reports (to prevent abuse)!')
    A.red.set('i.p.core.repu.%s' % obj.nick, 1)
    A.red.expire('i.p.core.repu.%s' % obj.nick, 600) 
    msg = ' '.join(obj.m[1:])
    id = A.red.incr('i.p.core.reportid')
    k = 'i.p.core.rep.%s' % id
    A.red.hset(k, 'user', obj.nick)
    A.red.hset(k, 'chan', obj._data.get('dest'))
    A.red.hset(k, 'msg', msg)
    A.red.hset(k, 'active', 1)
    for i in cfg.admin_chans:
        obj.send(i, 'NEW REPORT #%s FILED BY %s: %s' % (id, obj.nick, msg))
    return obj.reply('Your report (#%s) has been filed. Please be patient as we process it.' % id)

@P.cmd('rlist', admin=True, kwargs=True, kbool=['active'],
    usage='{cmd} active={bool}', desc="List all reports, use active bool to filter out closed reports.")
def cmdRlist(obj):
    obj.reply('ALL REPORTS:')
    for key in A.red.keys('i.p.core.rep.*'):
        if not int(A.red.hget(key, 'active')) and not obj.kwargs.get('active', False): continue
        msg = A.red.hget(key, 'msg')
        user = A.red.hget(key, 'user')
        chan = A.red.hget(key, 'chan')
        if chan: chan = '(from %s)' % chan
        else: chan = ''
        obj.reply('#%s: "%s" - %s %s' % (key.split('.')[-1], msg, user, chan))

@P.cmd('redit', admin=True, kwargs=True, kbool=['active', 'delete'],
    usage="{cmd} id active={bool} delete={bool}")
def cmdRedit(obj):
    if len(obj.m) < 2: return obj.usage()
    if not obj.m[1].isdigit(): return obj.reply('ID needs to be an integer (number)!')
    if not A.red.exists('i.p.core.rep.%s' % obj.m[1]): return obj.reply('No report with ID #%s!' % obj.m[1])

    if 'active' in obj.kwargs:
        A.red.hset('i.p.core.rep.%s' % obj.m[1], 'active', int(obj.kwargs.get('active')))
        return obj.reply('Report #%s is now %s' % (obj.m[1], {False:'[INACTIVE]', True:'[ACTIVE]'}[obj.kwargs.get('active', False)]))
    if obj.kwargs.get('delete', False):
        A.red.delete('i.p.core.rep.%s' % obj.m[1])
        return obj.reply('Report #%s deleted!' % obj.m[1])

