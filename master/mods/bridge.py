from api import A, Cmd, Hook

__NAME__ = "Bridge"
__VERSION__ = 0.1
__AUTHOR__ = "B1naryTh1ef"

options = {
    'bridges':[
        {
            'from':'#B0tT3st3r',
            'to':'#Testy1'
        }
    ],
}

key = dict([(i['from'], i['to']) for i in options['bridges']])

@Hook('chanmsg')
def chanmsgHook(obj):
    if obj.chan in key.keys():
        A.write(key[obj.chan], '<%s> %s' % (obj.user, obj.msg))

def onLoad(): pass
def onUnload(): pass