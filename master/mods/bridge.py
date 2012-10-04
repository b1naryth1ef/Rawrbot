from api import Cmd, Hook, A
from data import ConfigFile

__NAME__ = "Bridge"
__VERSION__ = 0.1
__AUTHOR__ = "B1naryTh1ef"

default_config = {
    'bridges':[
        {
            'server':1,
            'from':'b0tt3st',
            'to':'testy1'
        },
        {
            'server':1,
            'from':'testy1',
            'to':'b0tt3st'
        }
    ],
}

c = ConfigFile(name="bridge", default=default_config)

key = dict([(i.id, {}) for i in A.master.networks.values()])

for i in c.bridges:
    if i['from'] in key[i['server']]: key[i['server']][i['from']].append(i['to'])
    else: key[i['server']][i['from']] = [i['to']]


@Hook('chanmsg')
def chanmsgHook(obj):
    print obj.chan.lower(), obj.w.network.id, key
    if obj.chan.lower() in key[obj.w.network.id].keys():
        for i in key[obj.w.network.id][obj.chan.lower()]:
            obj.w.write(i, '<%s> %s' % (obj.user, obj.msg))

def onLoad(): pass
def onUnload(): pass