from api import Plugin, A

P = Plugin(A, "UrTTV", 0.1, "B1naryTh1ef")

GTV_COMMANDS = ['servers', 'addserver', 'rmvserver', 'editserver', 'seven']
GTV_PUB_COMMANDS = ["upcoming", "last", "suggest"]

def editGtvServer(id, kwargs):
    return A.red.hmset('i.p.urttv.server.%s' % id, kwargs)

def addGtvServer(kwargs):
    if not kwargs['id']:
        id = A.red.incr('i.p.urttv.serverid')
        kwargs['id'] = id
    return kwargs['id'], A.red.hmset('i.p.urttv.server.%s' % kwargs['id'], kwargs)

def getGtvServers():
    servers = []
    for key in A.red.keys('i.p.urttv.server.*'):
        servers.append(A.red.hgetall(key))
    return servers

def editMatch(id, kwargs): pass
def addMatch(kwargs): pass
def getMatches(): pass

#!gtv
#!gtv addserver ip=blah.blah.com pw=joinpw cam=campw admin=adminpw, host=blah
@P.cmd('gtv', usage='{cmd} <cmd> [args]', kwargs=True, chans=["urban-zone.radio", "urttv"])
def cmdGTV(obj):
    _usage = "!gtv addserver ip=127.0.0.1 cam=CAMPASS admin=ADMINPASS (not required:) pw=SERVERPASS host=HOSTERNAME"
    if len(obj.m) < 2: return obj.usage()
    if obj.m[1] not in GTV_COMMANDS+GTV_PUB_COMMANDS: return obj.reply('Unknown GTV command "%s"' % obj.m[1])
    if not obj.admin and obj.m[1] in GTV_COMMANDS: return obj.reply('You must be an admin to do that!')
    if obj.m[1] == 'seven' and obj.nick.lower() == 'sevenofnine': return obj.reply("You sexy thing <3")
    if obj.m[1] == 'servers':
        x = getGtvServers()
        if x and len(x):
            obj.reply('GTV Servers: ')
            for i in x:
                obj.smu("  #{id}: {ip} - PW: {pw} - Camera: {cam} - Admin: {admin} - Hoster: {host}".format(**i))
        else: return obj.reply('No GTV servers!')
    elif obj.m[1] == 'rmvserver':
        id = obj.kwargs.get('id')
        if not id and len(obj.m) > 2: id = obj.m[2]
        else: return obj.reply('ID must be an integer value!')
        if not id: return obj.reply('Usage: !gtv rmvserver id=0')
        if A.red.exists('i.p.urttv.server.%s' % id):
            A.red.delete('i.p.urttv.server.%s' % id)
            return obj.reply('Deleted server #%s successfully!' % id)
        else: return obj.reply('No server with ID #%s!' % id)
    elif obj.m[1] == 'addserver':
        if not obj.kwargs.get('ip') or not obj.kwargs.get('cam') or not obj.kwargs.get('admin'):
            return obj.reply("Usage: %s" % _usage)
        val = {}
        val['ip'] = obj.kwargs.get('ip')
        val['cam'] = obj.kwargs.get('cam')
        val['admin'] = obj.kwargs.get('admin')
        val['pw'] = obj.kwargs.get('pw')
        val['host'] = obj.kwargs.get('host')
        val['id'] = obj.kwargsg.get('oid', None)
        id, suc = addGtvServer(val)
        if suc: return obj.reply('Added GTV server #%s!' % id)
        else: return obj.reply('Failed to add GTV server!')
    elif obj.m[1] == 'editserver':
        if len(obj.m) < 3: return obj.reply('Usage: !editserver id ip=127.0.0.1 cam=CAMPASS admin=ADMINPASS pw=SERVERPASS host=HOSTERNAME')
        vals = {}
        for i in ['ip', 'cam', 'admin', 'pw', 'host']:
            if i in obj.kwargs.keys():
                vals[i] = obj.kwargs.get(i)
        if A.red.exists('i.p.urttv.server.%s' % obj.m[2]):
            if editGtvServer(obj.m[2], vals):
                return obj.reply('Edited server #%s successfully!' % obj.m[2])
            else:
                return obj.reply('Error editing server #%s!' % obj.m[2])
        else: return obj.reply('No server with ID #%s!' % obj.m[2])
    elif obj.m[1] == 'addmatch': pass
    elif obj.m[1] == 'rmvmatch': pass
    elif obj.m[1] == 'editmatch': pass
    elif obj.m[1] == 'matches': pass
