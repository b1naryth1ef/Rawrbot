from api import Cmd, Hook, A

__NAME__ = "Util"
__VERSION__ = 0.1
__AUTHOR__ = "B1naryTh1ef"

default_config = {}
config = ConfigFile(name="bridge", default=default_config)

@Cmd('msg')
def cmdMsg(obj): pass

def onLoad(): pass
def onUnload(): pass