import redis, json

red = redis.Redis(host="hydr0.com", password="")
sub = red.pubsub()

server = "irc.quakenet.org"
channels = {
    "B0tT3st":0,
}
workers = [] #@TODO Ping workers to keep this in sync

def getChan():
    r = []
    m = min(channels.values())
    for k, v in channels:
        if v != m: continue
        r.append(k)
    return r

class Worker(object):
    def __init__(self, wid):
        self.id = wid
        self.nick = "B1nB0t-%s" % wid
        self.chan = "irc.worker.%s"

        self.server = server
        
        self.active = True
        self.ping = 0

    def loop(self): pass

    def parse(self, msg):
        m = json.loads(msg)
        if m['tag'] == "BYE": self.kill()

    def send(self, tag, **kwargs):
        kwargs['tag'] = tag
        red.publish(self.chan, json.dumps(kwargs)) #@DEV If we want, we can eventually zlib this

    def kill(self):
        self.active = False
        workers[self.id] = None
