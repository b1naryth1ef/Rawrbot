# Just derpin
from api import Plugin, A

P = Plugin(A, "PugBot", 0.1, "B1naryTh1ef")

@P.cmd("testy")
def testy(obj):
    return obj.reply("Successful!")
