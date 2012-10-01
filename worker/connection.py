import sys, os, time
import socket

DEBUG = False

class Connection():
    def __init__(self, host=None, nick=None, port=6667):
        self.c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host
        self.nick = nick
        self.port = port

        self.alive = False
        self.connecting = False

    def connect(self, autojoin=[]):
        self.c.connect((self.host, self.port))
        self.connecting = True
        self.c.send('NICK %s\r\n' % self.nick)
        self.c.send('USER %s 0 * :WittleBoteh Hipstah\r\n' % self.nick)
        startPong = time.time()
        while time.time()-startPong < 10: #Wait only 10 seconds for a PING message
            x = self.read().strip()
            if 'PING' in x:
                self.write('PONG%s' % x.split('PING')[1])
                break
        startWait = time.time()
        while time.time() - startWait < 15:
            x = self.read().strip()
            if 'End of /MOTD' in x:
                self.alive = True
                self.connecting = False
                self.write('JOIN') #Junk message (is required sometimes, othertimes just throws an error we ignore)
                for i in autojoin:
                    self.write('JOIN #%s' % i)
                break
        if not self.alive: raise Exception("Could not connect to server '%s:%s'" % (self.host, self.port))
        return self

    def disconnect(self):
        self.c.close()
        self.alive = False

    def read(self, bytes=4080): 
        data = self.c.recv(bytes)
        if DEBUG: print data
        if data: return data
        return None

    def write(self, content):
        self.c.send('%s\r\n' % content)