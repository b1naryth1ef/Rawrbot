from api import Plugin, A
import time

P = Plugin(A, "Clans", 0.1, "B1naryTh1ef")

#REDIS
#i.p.clan.cw.CHANNEL (hash)
#i.p.clan.cw.LAST

#!cws practice=bool ignore=#chana, #chanb, #chanc
#!addcw players=X gm=CTF notes=blah blah blah
#[#owls-team] (PRACTICE) 5v5 TS: "My notes here"

def getID():
    return A.red.incr('i.p.clan.cwinc')

def genMessage(args):
    msg = []
    msg.append('CLAN WAR #{id}:')
    msg.append('[{chan}]')
    if args['practice']:
        msg.append('(PRACTICE)')
    msg.append('{nump}vs{nump}')
    if args['notes']: msg.append('{gm}: "{notes}"')
    else: msg.append('{gm}')
    return ' '.join(msg).format(**args)

def onLoad(): #@DEV stacks up, unload call?
    A.addConfig('clanspam')

def onUnload():
    A.rmvConfig('clanspam')

@P.apih('clan_spam_msg')
def clanSpam(net, msg, force):
    attempts, success = 0, 0
    for chan in A.red.smembers('i.%s.chans' % net):
        attempts += 1
        _v = A.red.get('i.%s.chan.%s.cfg.clanspam' % (net, chan))
        if _v and not int(_v): continue
        A.write(net, chan, msg)
        success += 1
    return attempts, success

def getClanWars():
    res = []
    for key in A.red.keys('i.p.clan.cw.*'):
        if not A.red.type(key) == 'hash': continue #get around 'NULL' keys
        res.append(A.red.hgetall(key))
    return res

@P.cmd('cws', usage="{cmd} practice={bool}", kwargs=True, kbool=['practice'])
def cmdCWS(obj):
    res = getClanWars()
    if len(res):
        obj.reply('Clan Wars: ')
        for cw in res:
            if obj.kwargs.get('practice') and not obj.kwargs.get('practice') == cw['practice']: continue
            obj.smu('  '+genMessage(cw))
            time.sleep(0.3)
    else:
        obj.reply('No clan wars!')

@P.cmd('addcw', usage="{cmd} practice={bool} players=X gm=CTF/TS/BOMB notes=This is an awesome clan war opportunity!", kwargs=True, kbool=['practice'])
def cmdAddCw(obj):
    if not obj.op:
        return obj.reply("You must be an admin of the channel to request a cw or pcw!")
    if not 'players' in obj.kwargs or not 'gm' in obj.kwargs: return obj.usage()
    if A.red.exists('i.p.clan.cw.%s' % obj.dest):
        return obj.reply("You've already spammed a cw or pcw in the past 15 minutes! Please wait before spamming again!")
    if not obj.kwargs.get('players').isdigit():
        return obj.reply("Players must be an INTEGER value (a number ;D)")
    cw = {'nump': obj.kwargs.get('players'),
        'gm': obj.kwargs.get('gm'),
        'notes': obj.kwargs.get("notes"),
        'practice': obj.kwargs.get('practice', False),
        'chan': obj.dest,
        'id': getID()}
    A.red.hmset('i.p.clan.cw.%s' % obj.dest, cw)
    A.red.expire('i.p.clan.cw.%s' % obj.dest, 900)
    a, s = A.callHook('clan_spam_msg', obj.nid, genMessage(cw), False)
    obj.reply('Your clan (ID #%s) war was spammed to %s out of %s channels!' % (cw['id'], s, a))

@P.cmd('rmvcw')
def cmdRmvCw(obj):
    s = 'i.p.clan.cw.%s' % obj.dest
    if not A.red.exists(s):
        return obj.reply('No spam exists for this channel!')
    delay = A.red.ttl(s)
    A.red.delete(s)
    A.red.set(s, 'NULL')
    A.red.expire(s, delay)
    obj.reply('Deleted your current clan war!')
