from api import A, Cmd, Hook
from mechanize import Browser
import re

__NAME__ = "Web"
__VERSION__ = 0.1
__AUTHOR__ = "B1naryTh1ef"

options = {
}

br = Browser()

@Hook('chanmsg')
def chanmsgHook(obj):
	if '.' in obj.msg: #Dont regex search everything plz
		r = re.findall(r'([http://|https://][^\"\' ]+)', obj.msg)
		if len(r):
			for i in r:
				try: 
					if not i.startswith('http'):
						i = "http://"+i
					br.open(i)
					if not br.title(): continue
					A.write(obj.chan, "%s: %s" % (i, br.title()))
				except: pass

def onLoad(): pass
def onUnload(): pass