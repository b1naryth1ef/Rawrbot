from api import Plugin, A
from pkgs import rcon
import socket
import struct

print 'Loaded!'

class MCQuery(): #Based off https://github.com/barneygale/MCQuery/
    id = 0
    def __init__(self, host, port):
        self.addr = (host, int(port))
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.handshake()
    
    def write_packet(self, type, payload):
        o = '\xFE\xFD' + struct.pack('>B', type) + struct.pack('>l', self.id) + payload
        self.socket.sendto(o, self.addr)
    
    def read_packet(self):
        buff = self.socket.recvfrom(2048)[0]
        type = struct.unpack('>B', buff[0])[0]
        id   = struct.unpack('>l', buff[1:5])[0]
        return type, id, buff[5:]
    
    def handshake(self):
        self.id += 1
        self.write_packet(9, '')
        try:
            type, id, buff = self.read_packet()
        except:
            print 'Could not connect!'
            return False
        
        self.challenge = struct.pack('>l', int(buff[:-1]))
    
    def full_stat(self):
        self.write_packet(0, self.challenge + '\x00\x00\x00\x00')
        try:
            type, id, buff = self.read_packet()
        except:
            if not self.handshake(): return False
            return self.full_stat()    
        buff = buff[11:]
        items, players = buff.split('\x00\x00\x01player_\x00\x00')
        items = 'motd' + items[8:] 
        items = items.split('\x00')
        data = dict(zip(items[::2], items[1::2])) 
        players = players[:-2]
        if players: data['players'] = players.split('\x00')
        else:       data['players'] = []
        for k in ('numplayers', 'maxplayers', 'hostport'):
            data[k] = int(data[k])
        return data

P = Plugin(A, "Utils", 0.1, "B1naryTh1ef")

@P.cmd('urt', usage="{cmd} [IP/Host[:port]]", desc="Get info for a UrT Server")
def cmdUrt(obj):
    if len(obj.m) < 2: return obj.usage()
    if ':' in obj.m[1]: host, port = obj.m[1].split(':', 1)
    else: 
        host = obj.m[1]
        port = 27960
    o = rcon.RCON(server=host, port=int(port), password="").getstatus()
    print o

@P.cmd('mc', usage="{cmd} [IP/Host[:port]]", desc="Get info for a mc server (needs to have querying enabled!)")
def cmdMc(obj):
    if len(obj.m) < 2: return obj.usage()
    if ':' in obj.m[1]: host, port = obj.m[1].split(':', 1)
    else: 
        host = obj.m[1]
        port = 25565
    o = MCQuery(host, port).full_stat()
    if not o: return obj.reply('Failed to connect to server "%s:%s"' % (host, port))
    else:
        obj.reply('%s:%s is running MC V%s w/ %s players on %s' % (host, port, o['version'], o['numplayers'], o['gametype']))
        obj.reply('MOTD: %s' % o['motd'])
        obj.reply('Players: %s' % (', '.join(o['players'])))

@P.cmd('ts3', usage="{cmd} [IP/Host]", desc="Get info for a TS3 server")
def cmdTs3(obj): pass