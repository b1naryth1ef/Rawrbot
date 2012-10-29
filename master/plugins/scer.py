#FOR _BOTH_ MUSIC and VIDEO (URT SC's)
from api import Plugin, A
from data import ConfigFile
import sys, os, time
import requests

P = Plugin(A, "Shoutcaster", 0.1, "B1naryTh1ef")

default_cfg = {
    'channels':[{
        'name':'Urban Zone',
        'id':'urbanzone',
        'nid':0,
        'chan':'urban-zone.radio',
        'spam':True,
        'spams':[{
            'chans':['urban-zone', 'b1naryth1ef', 'urt-tv'],
            'delay':10
        },
        {
            'chans':['urban-terror'],
            'delay':20
        }]
    }]
}

config = ConfigFile(name="scer", default=default_cfg, path=['plugins', 'config'])
ELIVE = "http://api.justin.tv/api/stream/list.json?channel=%s"
 
def getStreamInfo(id):
    try:
        return requests.get(EINFO % id).json
    except:
        print 'Could not grab Justin.tv info API for %s' % id

@P.cmd('scfg', admin=True)
def cmdScfg(obj): pass

@P.loop(120)
def coreLoop():
    for chan in config.channels:
        try: r = requests.get(ELIVE % chan['id']).json
        except: 
            print 'Could not grab Justin.tv API for %s' % chan['id']
            continue
        if len(r):
            msg = '%S IS LIVE NOW: %s' % (chan['name'].upper(), r[0]['title'])
            spams = []
            A.red.set('i.p.scer.%s.live' % chan['id'], 1)
            if config.spam:
                for spam in config.spams:
                    spams.append(A.callHook('core_spam_add', data['nid'], msg, spam['chans'], -1, spam['delay'], active=0))
            A.write(chan['nid'], chan['chan'], "The stream '%s' has gone live!" % chan['name'])
            if len(spams):
                A.write(chan['nid'], chan['chan'], "Automatically added the following (inactive) spams: %s" % (', '.join(spams)))
        elif not len(r):
            i = A.red.get('i.p.scer.%s.live' % chan['id'])
            if i and int(i):
                A.red.set('i.p.scer.%s.live' % chan['id'], 0)
                A.write("The stream '%s' has stop broadcasting!" % chan['name'])

