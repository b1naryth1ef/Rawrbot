from api import Plugin, A

P = Plugin(A, "UrTTV", 0.1, "B1naryTh1ef")

GTV_COMMANDS = ['servers', 'addserver', 'rmvserver']

def addGtvServer(kwargs):
    id = A.red.incr('i.p.urttv.serverid')
    return id, A.red.hmset('i.p.urttv.server.%s' % id, kwargs)

def getGtvServers():
    servers = []
    for key in A.red.keys('i.p.urttv.server.*'):
        servers.append(A.red.hgetall(key))
    return servers

#!gtv
#!gtv addserver ip=blah.blah.com pw=joinpw cam=campw admin=adminpw, host=blah
@P.cmd('.gtv', admin=True, usage='{cmd} <cmd> [args]', kwargs=True) #the . is for compatability right now
def cmdGTV(obj):
    _usage = "!gtv addserver ip=127.0.0.1 cam=CAMPASS admin=ADMINPASS (not required:) pw=SERVERPASS host=HOSTERNAME"
    if len(obj.m) < 2: return obj.usage()
    if obj.m[1] not in GTV_COMMANDS:
        return obj.reply('Unknown GTV command "%s"' % obj.m[1])
    if obj.m[1] == 'servers':
        x = getGtvServers()
        if x and len(x):
            obj.reply('GTV Servers: ')
            for inc, i in enumerate(x):
                i['id'] = inc+1
                obj.smu("#{id}: {ip} PW: {pw} Camera: {cam} Admin: {admin} Hoster: {host}".format(**i))
        else:
            return obj.reply('No GTV servers!')
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
        id, suc = addGtvServer(val)
        if suc: return obj.reply('Added GTV server #%s!' % id)
        else: return obj.reply('Failed to add GTV server!')
