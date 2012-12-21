from api import Plugin, A
import time

P = Plugin(A, "Clans", 0.1, "B1naryTh1ef")

#REDIS
#i.p.clan.cw.CHANNEL (hash)
#i.p.clan.cw.LAST

#!cws practice=bool ignore=#chana, #chanb, #chanc
#!addcw players=X gm=CTF notes=blah blah blah

def genMessage(args):
    msg = []
    msg.append('[{chan}]')
    if args['practice']:
        msg.append('(PRACTICE)')
    msg.append('{nump}vs{nump} {gm}')
    if args['notes']:
        msg.append(': {notes}')
    return ' '.join(msg).format(**args)

def onLoad():
    A.addConfig('clanspam')

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
        res.append(A.red.hgetall(key))
    return res

@P.cmd('cws', usage="{cmd} practice={bool}", kwargs=True, kbool=['practice'])
def cmdCWS(obj):
    obj.reply('Clan Wars: ')
    for cw in getClanWars()[30:]:
        obj.smu('  '+genMessage(cw))
        time.sleep(0.3)
# [#owls-team] (PRACTICE) 5v5 TS: "My notes here"

@P.cmd('addcw', usage="{cmd} practice={bool} players=X gm=CTF/TS/BOMB notes=This is an awesome clan war opportunity!", kwargs=True, kbool=['practice'])
def cmdAddCw(obj):
    if not obj.op:
        return obj.reply("You must be an admin of the channel to request a cw or pcw!")
    if not 'players' in obj.kwargs or not 'gm' in obj.kwargs: return obj.usage()
    if A.red.exists('i.p.clan.cw.%s' % obj.chan):
        return obj.reply("You've already spammed a cw or pcw in the past 15 minutes! Please wait before spamming again!")
    cw = {'nump': obj.kwargs.get('players'),
        'gm': obj.kwargs.get('gm'),
        'notes': obj.kwargs.get("notes"),
        'practice': obj.kwargs.get('practice', False),
        'chan': obj.chan}
    A.red.hmset('i.p.clan.cw.%s' % obj.chan, cw)
    A.red.expire('i.p.clan.cw.%s' % obj.chan, 900)
    a, s = A.callHook('clan_spam_msg', obj.nid, genMessage(cw))
    obj.reply('Your clan war was spammed to %s out of %s channels!' % (s, a))
