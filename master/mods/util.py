from api import Cmd, Hook, A
from data import ConfigFile

__NAME__ = "Util"
__VERSION__ = 0.2
__AUTHOR__ = "B1naryTh1ef"

default_config = {}
config = ConfigFile(name="util", path=['mods', 'config'], default=default_config)

@Cmd('msg', kwargs=True, kwargsbool=['nick'])
def cmdMsg(obj):
    obj.sess['msg'] = obj.kwargs.get('msg', ' '.join(obj.m[1:]))
    obj.sess['chan'] = obj.kwargs.get('chan', obj.dest).lower()
    obj.sess['nick'] = obj.kwargs.get('nick', True)
    if obj.sess['nick']: obj.sess['msg'] = "%s: %s" % (obj.nick, obj.sess['msg'])
    if not obj.w.network.hasChan(obj.sess['chan']) and obj.sess['chan'] != '*':
        return obj.send(obj.dest, "%s: The bot is not joined too %s" % (obj.nick, obj.sess['chan']))
    else: obj.msg = obj.sess['msg']
    if obj.sess['chan'] == '*': obj.w.network.writeGlobal(obj.msg)
    else: obj.send(obj.sess['chan'], obj.msg)

def onLoad(): pass
def onUnload(): pass