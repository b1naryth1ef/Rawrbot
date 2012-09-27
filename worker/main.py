import redis, json
import random

class Worker(object):
    def __init__(self):
        self.id = -1
        self.nick = ""
        self.channels = []
        self.server = ""

        self.red = redis.Redis(host="hydr0.com", password="")
        self.sub = self.red.pubsub()

        self.boot()
        self.active = True
        self.loop()

    def loop(self):
        self.sub.subscribe("irc.worker.%s" % self.id)
        while self.active:
            for msg in sub.listen():
                print msg
        self.sub.unsubscribe("irc.worker.%s" % self.id)

    def boot(self):
        print 'Attempting to boot worker...'
        resp = "irc.%s" % random.randint(1111, 9999) #Get a random channel int
        self.sub.subscribe(resp)
        self.push("HI", resp=resp)
        while True:
            for msg in self.sub.listen():
                obj = json.loads(msg['data'])
                self.__dict__.update(obj)
                print 'Worker booted!'
        self.sub.unsubscribe(resp)

    def push(self, tag, **kwargs): #Push a message to master
        kwargs['tag'] = tag
        self.red.publish("irc.master", json.dumps(kwargs))

w = Worker()