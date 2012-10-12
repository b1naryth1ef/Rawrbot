from api import Cmd, Hook, A
from data import ConfigFile
import re

__NAME__ = "Web"
__VERSION__ = 0.1
__AUTHOR__ = "B1naryTh1ef"

options = {
}

config = ConfigFile(name="web", path=['mods', 'config'], default=options)

@Hook('chanmsg')
def chanmsgHook(obj): pass

def onLoad(): pass
def onUnload(): pass