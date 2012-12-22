from api import Plugin, A
from data import ConfigFile

P = Plugin(A, "Admin", 0.1, "B1naryTh1ef")

default_cfg = {
    'admin_chans': ['b1naryth1ef', 'rawrbot.admins']
}

cfg = ConfigFile(name='admin', path=['plugins', 'config'], default=default_cfg)

@P.apih('admin_add_report')
def adminAddReport(msg, nick, chan, net):
    id = A.red.incr('i.p.core.reportid')
    k = 'i.p.core.rep.%s' % id
    A.red.hset(k, 'user', nick)
    A.red.hset(k, 'chan', chan)
    A.red.hset(k, 'msg', msg)
    A.red.hset(k, 'active', 1)
    for i in cfg.admin_chans:
        if chan: c = '[%s]' % chan
        else: c = ''
        A.write(net, i, 'NEW REPORT #%s FILED BY %s: %s %s' % (id, nick, msg, c))
    return True, id

@P.apih('admin_edit_report')
def adminEditReport(): pass

@P.hook('BAN_W')
def hookBanWorker(obj):
    adminAddReport('Worker banned from channel!', obj.nick, obj.chan, obj.nid)

@P.hook('KICK_W')
def hookKickWorker(obj):
    if A.red.exists('i.p.core.kickw.%s' % obj.kicked):
        x = A.red.get('i.p.core.kickw.%s' % obj.kicked)
        if int(x) >= 10: #Got kicked 5 times
            #@TODO Assign another worker or remove channel from list
            A.red.set('i.p.core.kickw.%s' % obj.kicked, 0)
            return adminAddReport('Worker being continuely kicked from channl!', obj.kicked, obj.chan, obj.nid)
        else:
            A.red.incr('i.p.core.kickw.%s' % obj.kicked)
            A.red.expire('i.p.core.kickw.%s' % obj.kicked, 600) #Key expires in 10 minutes
            return #This prevents spamming reports
    if not obj.msg: obj.msg = "No Message"
    A.red.set('i.p.core.kickw.%s' % obj.kicked, 1)
    adminAddReport('Worker kicked from channel: %s' % obj.msg, obj.kicked, obj.chan, obj.nid)

@P.cmd('kick', admin=True, usage='{cmd} <user> msg=msg', kwargs=True, desc="Kick a user from your channel, with an optional message.")
def cmdKick(obj):
    if len(obj.m) < 2:
        return obj.usage()
    if obj.isBotOp():
        return obj.raw('KICK %s %s :%s' % (obj.dest, obj.m[1], obj.kwargs.get('msg', '')))
    obj.reply('The bot is not an operator, and as such cannot complete your command!')

@P.cmd('bug', admin=True, usage='{cmd} <msg>', desc="Report a bug!")
def cmdBug(obj):
    if len(obj.m) < 2: return obj.usage()
    if not obj.op: return obj.reply('Sorry, but only channel ops can submit bug reports (This is to reduce spam! If the problem is urgent, use !report)')
    result, id = adminAddReport('[BUG]'+obj.m[1:], obj.nick, obj._data.get('dest'), obj.nid)
    if not result: return obj.reply("There was an error filing your bug (Ironic isnt it?)")
    return obj.reply("Your bug report was filed! (For reference, its bug report #%s!)" % id)

@P.cmd('report', usage='{cmd} <my message to admins>',
    desc="Send a message to the admins (IN ENGLISH), or ask for assistance. (Abuse results in banz!)")
def cmdReport(obj):
    if len(obj.m) < 2:
        return obj.reply('Please specify a message to describe the problem your having (in english)!')
    if not obj.admin and A.red.get('i.p.core.repu.%s' % obj.nick): #This isnt horribly secure, but w/e
        return obj.reply('Please wait 10 minutes in between sending reports (to prevent abuse)!')
    A.red.set('i.p.core.repu.%s' % obj.nick, 1)
    A.red.expire('i.p.core.repu.%s' % obj.nick, 600)
    msg = ' '.join(obj.m[1:])
    result, id = adminAddReport(msg, obj.nick, obj._data.get('dest'), obj.nid)
    if not result:
        return obj.reply("There was an error filing your report!")
    return obj.reply('Your report (#%s) has been filed. Please be patient as we process it.' % id)

@P.cmd('rlist', gadmin=True, kwargs=True, kbool=['active'],
    usage='{cmd} active={bool}', desc="List all reports, use active bool to filter out closed reports.")
def cmdRlist(obj):
    if not len(A.red.keys('i.p.core.rep.*')): return obj.reply("No reports!")
    obj.reply('ALL REPORTS:')
    for key in A.red.keys('i.p.core.rep.*'):
        if not int(A.red.hget(key, 'active')) and not obj.kwargs.get('active', False): continue
        msg = A.red.hget(key, 'msg')
        user = A.red.hget(key, 'user')
        chan = A.red.hget(key, 'chan')
        if chan: chan = '(from %s)' % chan
        else: chan = ''
        obj.reply('#%s: "%s" - %s %s' % (key.split('.')[-1], msg, user, chan))

@P.cmd('redit', gadmin=True, kwargs=True, kbool=['active', 'delete'],
    usage="{cmd} id active={bool} delete={bool}", desc="Edit a report.")
def cmdRedit(obj):
    if len(obj.m) < 2: return obj.usage()
    if not obj.m[1].isdigit(): return obj.reply('ID needs to be an integer (number)!')
    if not A.red.exists('i.p.core.rep.%s' % obj.m[1]): return obj.reply('No report with ID #%s!' % obj.m[1])

    if 'active' in obj.kwargs:
        A.red.hset('i.p.core.rep.%s' % obj.m[1], 'active', int(obj.kwargs.get('active')))
        return obj.reply('Report #%s is now %s' % (obj.m[1], {False: '[INACTIVE]', True: '[ACTIVE]'}[obj.kwargs.get('active', False)]))
    if obj.kwargs.get('delete', False):
        A.red.delete('i.p.core.rep.%s' % obj.m[1])
        return obj.reply('Report #%s deleted!' % obj.m[1])
