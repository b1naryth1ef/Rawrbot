##[BEGIN - Import]##
import socket
import IN
import struct
import sys
import random
import MySQLdb
import os
import re
import string
import urllib2
import urllib
from time import ctime
from time import sleep
from threading import Thread
import traceback
##[END - Import]##

##[BEGIN - Global Settings]##
host = "irc.quakenet.org"
#host = "clanserver4u2.de.quakenet.org"
#host = "port80.se.quakenet.org"
#port = 6665 <-- wird nicht mehr benutzt in den klassen jeweils self.port = random.choice([6665,6666,6668,6669])
pub_chan = "#peng"
priv_chan = "#peng.ubber.priv"
admin_chan = "#peng.private"

db_host = "localhost"
db_user = "1_pengbotuser"
db_passwd = "L0k0m0tive"
db_db = "1_pengbot"

db1_host = db_host
db1_user = db_user
db1_passwd = db_passwd 
db1_db = "2_pengbot_urtstats" 

OWNER="~gost0r@Gost0r.users.quakenet.org Liquid@bot.pengbot.de"

threads = {}
##[END - Global Settings]##


##[BEGIN - Other Settings]##
print "initing values..."
sleep(2)

version         = "v2.1"                #botversion

cmd_prefix      = "!"                   #cmd prefix
pickup_prefix   = "pickup"              #pickup prefix

submit_pcw      = "pcw"                 #cmd submit pcw
submit_cw       = "cw"                  #cmd submit cw
submit_ringer   = "ringer"              #cmd submit ringer
submit_recruit  = "recruit"             #cmd submit ringer
submit_msg      = "msg"                 #cmd submit msg
submit_gtv      = "gtvmsg"              #cmd submit msg

list_pcw        = "pcwlist"             #cmd list pcw
list_cw         = "cwlist"              #cmd list cw
list_ringer     = "ringerlist"          #cmd list ringer
list_recruit    = "recruitlist"         #cmd list ringer
list_msg        = "msglist"             #cmd list msg
list_gtv        = "gtvlist"             #cmd list msg

show_pcw        = "displaypcw"          #cmd display pcw
show_cw         = "displaycw"           #cmd display cw
show_ringer     = "displayringer"       #cmd display ringer
show_recruit    = "displayrecruit"      #cmd display ringer
show_msg        = "displaymsg"          #cmd display msg
show_gtv        = "displaygtv"          #cmd display msg

show_status     = "status"              #cmd show enable spaming settings

enable_pickup   = "displaypickup"       #cmd enable pickup
pickup_remove   = "remove"              #pickup remove
pickup_maps     = "maps"                #pickup maplist
pickup_modes    = "modes"               #pickup modelist
pickup_vote     = "vote"                #pickup vote map/mode
pickup_pw       = "pw"                  #pickup lostpassword

pickup_add      = "add"                 #pickup add
pickup_gameover = "gameover"            #pickup gameover
pickup_status   = "status"              #pickup status
pickup_players  = "players"             #pickup playerlist
pickup_help     = "help"                #pickup help

finder_prefix   = "find"                #find prefix
finder_name     = "name"                #find servername
finder_ip       = "ip"                  #find serverip
finder_player   = "player"              #find playername

info_gameover   = "#GAMEOVER#"          #pickup
info_datasent   = "#DATASENT#"          #pickup
info_sentto     = "#SENTTO#"            #pickup
info_signup     = "#SIGNUP#"            #pickup
info_update     = "#UPDATE#"            #pickup
info_pm         = "#PM#"                #pickup

sup_join        = "#JOIN#"              #Mastermsg joining
sup_spam        = "#SPAM#"              #Mastermsg spaming
sup_remove      = "#REMOVE#"            #Mastermsg removing

bot_new         = "#NEW#"               #Send to Master something new arrived -> bot_new kind id

spam_pcw        = "[PCW] .channel. - .nick. - Requesting a .number. vs .number. .start.(Additional info: .info.)"
spam_cw         = "[CW] .channel. - .nick. - Requesting a .number. vs .number. .start.(Additional info: .info.)"
spam_ringer     = "[RINGER] .channel. - .nick. - Requesting .number. .start.(Additional info: .info.)"
spam_recruit    = "[RECRUIT] .channel. - .nick. - Requesting .number. .start.(Additional info: .info.)"
spam_msg        = "[MSG] .channel. - .nick. - .info."
spam_gtv        = "[GTV] .channel. - .nick. - .info."
spam_amsg       = "[ADMINMSG] .channel. - .nick. - .info."

no_access_msg   = "[MSG] No access to use it"
no_access_gtv   = "[GTV] No access to use it"

display_pcw     = "[PCWLIST] .channel. - .nick. - Requesting a .number. vs .number. .start.(Additional info: .info.) .end.- .time. minutes ago"
display_cw      = "[CWLIST] .channel. - .nick. - Requesting a .number. vs .number. .start.(Additional info: .info.) .end.- .time. minutes ago"
display_ringer  = "[RINGERLIST] .channel. - .nick. - Requesting .number. .start.(Additional info: .info.) .end.- .time. minutes ago"
display_recruit = "[RECRUITLIST] .channel. - .nick. - Requesting .number. .start.(Additional info: .info.) .end.- .time. minutes ago"
display_msg     = "[MSGLIST] .channel. - .nick. - .info. - .time. minutes ago"
display_gtv     = "[GTVLIST] .channel. - .nick. - .info. - .time. minutes ago"

pkup_lock       = "[PICKUP] This game is currently locked"
pkup_nchan      = "[PICKUP] This channel doesn\'t support pickup."
pkup_para       = "[PICKUP] Not enough Parameter given. Try !pickup help"
pkup_map        = "Map was successfully voted." #'[PICKUP] ' added automaticly
pkup_mode       = "Mode was successfully voted." #'[PICKUP] ' added automaticly
pkup_mm         = "[PICKUP] You have already voted or Maps/Modes are not available."
pkup_signup     = "[PICKUP] You can sign up again!"
pkup_pw         = "[ /connect .server. ; password .password. ]"
pkup_gameover_a = "[PICKUP] Thanks for submit, .nick.! Need .gameoverleft. more players to confirm that the match is over!"
pkup_gameover_b = "[PICKUP] .nick. has requested Gameover! Need .gameoverleft. more players to confirm that the match is over!"
pkup_players    = "[PICKUP] Players [.playernumber./10]: .playerlist."
pkup_status1    = "[PICKUP] Sign up: [.playernumber./10] Type !pickup players to see who\'s signed up."
pkup_status2    = "[PICKUP] Nobody has signed up. Type !pickup add to play."
pkup_started    = "[PICKUP] Game already started. End time: .time. CET"
pkup_go_cap     = "Pickup starts now and you are Captain! You play .type. on the map .map.. Connect to the server and have a 1on1 knife fight against .captain. The winner can choose first! [ /connect .server. ; password .password. ]"
pkup_go_player  = "Pickup starts now! You play .type. on the map .map.. Connect to the server and stay as spectator until you are chosen by a Captain! [ /connect .server. ; password .password. ]"
pkup_go_sent    = "[PICKUP] Pichup has started and data was sent. You didn\'t recive ip/password? Type !pickup pw to get it!"

url_help        = "List of commands: http://pengbot.de/index.php?id=cmd"

not_auth        = "Trying to lookup your auth. If you are authed, resubmit the command."
not_oped        = "You need to be opped, to use this function."
is_banned       = "You are banned of using this function."
not_added       = "You are not added to use this function."
already_added   = "You are already added."
already_gameover= "You cant\'t sumbit gameover twice."
no_map_added    = "No maps available."
no_mode_added   = "No modes available."
error           = "There was an error in your command."

msg_enable      = "enablemsg"           #cmd enable msg
msg_disable     = "disablemsg"          #cmd disable msg

gtv_enable      = "enablegtv"           #cmd enable gtv
gtv_disable     = "disablegtv"          #cmd disable gtv

chan_add        = "add"                 #cmd add channel
chan_remove     = "remove"              #cmd remove channel

bot_add         = "newbot"              #cmd add bot
bot_delete      = "delbot"              #cmd remove bot

cmd_log         = "log"                 #cmd log

ban_add         = "newban"              #cmd add ban
ban_delete      = "delban"              #cmd remove ban

q_list          = "qlist"               #cmd request list
q_accept        = "qaccept"             #cmd request accept
q_refuse        = "qrefuse"             #cmd request refuse
q_del           = "qdel"                #cmd request refuse
q_refuseall     = "qrefuseall"          #cmd request refuseall

pickup_prefix   = "pickup"              #cmd prefix
pickup_lock     = "lock"                #Locks a game
pickup_unlock   = "unlock"              #Unlocks a game
pickup_reset    = "reset"               #Resets a game
pickup_getdata  = "getdata"             #Sends the ip + pw per pm to the admin
pickup_addmap   = "addmap"              #Adds a new map
pickup_delmap   = "delmap"              #Removes a map
pickup_addmode  = "addmode"             #Adds a new mode
pickup_delmode  = "delmode"             #Removes a mode
pickup_server   = "server"              #Changes a server
pickup_test     = "test"                #Sets the player number

pkup_pw         = "[ /connect .server. ; password .password. ]"
pkup_go_admin   = "Captains: .captain1. .captain2. - Password: .password. - Gametype: .type. - Map: .map."
requestinfo     = "There are .number. open channel requests."

url             = "http://urtgamerz.de/requestdenied.php"  #php for email
peng_url        = "http://urtgamerz.de/rconbot.php?ip=178.79.129.6&port=27960&password=NUbILJcs&rcon="   #php for rcon

lastrequest = ''
##[END - Other Settings]##

##[BEGIN - PengMaster Class]##
class botMaster(Thread):
    def __init__(self, useprint):
        Thread.__init__(self)
        self.useprint = useprint
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        self.host = host
        self.port = random.choice([6665,6666,6668,6669])
	self.nick = "pengMaster"
        self.realname = "pengMaster v2"
        self.identt = "pengMaster"
        self.readbuffer = ""
        
        self.mysql = MySQLdb.connect (host = db_host,
                                 user = db_user,
                                 passwd = db_passwd,
                                 db = db_db)
        self.cursor = self.mysql.cursor()
        
    def reportThreadStats(self, botNum):
        self.s.send('PRIVMSG ' + priv_chan + ' :Thread ' + botNum + ' closed after Throtteling\n')
    def restartThread(self, botNum):
        self.s.send('PRIVMSG ' + priv_chan + ' :restarting ' + botNum + '\n')
        threads[botNum].start()
    def requeststatus(self):
        count = "1"
        self.cursor.execute("SELECT id FROM 1_peng_requests WHERE handle='0' ORDER BY id DESC")
        peng = self.cursor.fetchall()
        if count == "1":
            count = "2"
            lastrequest = ""
            
        if len(peng) > 0:
            if lastrequest != peng[0][0]:
                lastrequest = peng[0][0]
                s_requestinfo = requestinfo.replace(".number.", str(len(peng)))
#                self.s.send('PRIVMSG ' + pub_chan + ' :' + s_requestinfo + '\n')
               
    def normalize_day(self, day):
        if len(day) == 1:
            return "0" + day
        else:
            return day

    def text_addinfo(self, data, start):
        stop = 0
        num = start
        what = ""
        lenge = len(data)
        while(stop < 1):
            if num == start:
                what = data[int(num)]
            else:
                what = what + " " + data[int(num)]
                num = int(num) + 1
            if int(num) == int(lenge):
                stop = 1
            if "\'" in what:
                what = what.replace("\'", "`")
            return what

    def auto_delete(self, gettime, getdate):
        self.cursor.execute("SELECT * FROM 1_peng_messages WHERE active='free'")
        peng = self.cursor.fetchall()
        lenpeng = len(peng) - 1
        stop = 0
        while (stop < 1):
            if lenpeng >= 0:
                peng1 = peng[int(lenpeng)]
                pengtime = peng1[9]
                pengtime = pengtime.split(":")
                pengmin = int(pengtime[1]) + 30
                if pengmin >= 60:
                    pengmin = pengmin - 60
                    pengtime[0] = int(pengtime[0]) + 1
                    if pengmin <= 9:
                        pengmin = "0" + str(pengmin)
                    if pengtime[0] <= 9:
                        pengtime[0] = "0" + str(pengtime[0])
                pengtime = str(pengtime[0]) + str(pengmin) + str(pengtime[2])
                newtime = gettime.split(":")
                newtime = newtime[0] + newtime[1] + newtime[2]
                if newtime < 3100:
                    newtime = newtime + 240000
                pengdate = peng1[8].split(".")
                pengdate = pengdate[2] + pengdate[1] + pengdate[0]
                newdate = getdate.split(".")
                newdate = newdate[2] + newdate[1] + newdate[0]
                newtime = newdate + newtime
                pengtime = pengdate + pengtime
                if newtime >= pengtime:
                    self.cursor.execute("UPDATE 1_peng_messages SET active='no' WHERE id='" + str(peng1[0]) + "'")
            else:
                stop = 1
            lenpeng = lenpeng - 1

    def auto_blocked(self, gettime, getdate):
        self.cursor.execute("SELECT * FROM 1_peng_messages WHERE active='yes'")
        peng = self.cursor.fetchall()
        lenpeng = len(peng) - 1
        stop = 0
        while (stop < 1):
            if lenpeng >= 0:
                peng1 = peng[int(lenpeng)]
                pengtime = peng1[9]
                pengtime = pengtime.split(":")
                pengmin = int(pengtime[1]) + 10
                if pengmin >= 60:
                    pengmin = pengmin - 60
                    pengtime[0] = int(pengtime[0]) + 1
                    if pengmin <= 9:
                        pengmin = "0" + str(pengmin)
                    if pengtime[0] <= 9:
                        pengtime[0] = "0" + str(pengtime[0])
                pengtime = str(pengtime[0]) + str(pengmin) + str(pengtime[2])
                newtime = gettime.split(":")
                newtime = newtime[0] + newtime[1] + newtime[2]
                if newtime < 3100:
                    newtime = newtime + 240000
                pengdate = peng1[8].split(".")
                pengdate = pengdate[2] + pengdate[1] + pengdate[0]
                newdate = getdate.split(".")
                newdate = newdate[2] + newdate[1] + newdate[0]
                newtime = newdate + newtime
                pengtime = pengdate + pengtime
                if newtime >= pengtime:
                    self.cursor.execute("UPDATE 1_peng_messages SET active='free' WHERE id='" + str(peng1[0]) + "'")
            else:
                stop = 1
            lenpeng = lenpeng - 1

    def peng_endtime(self, time, date):
        time = time.split(":")
        hour = time[0]
        minute = int(time[1]) + 30
        sec = time[2]
        date = date.split(".")
        year = date[2]
        month = date[1]
        day = date [0]
        if int(minute) >= 60:
            minute = minute - 60
            hour = int(hour) + 1
            if int(hour) >= 24:
                hour = 0
                day = int(day) + 1
            if int(day) > 31 and (int(month) == 1 or int(month) == 3 or int(month) == 5 or int(month) == 7 or int(month) == 8 or int(month) == 10 or int(month) == 12):
                day = 1
                month = int(month) + 1
            if int(day) > 30 and (int(month) != 1 and int(month) != 2 and int(month) != 3 and int(month) != 5 and int(month) != 7 and int(month) != 8 and int(month) != 10 and int(month) != 12):
                day = 1
                month = int(month) + 1
            if int(day) > 28 and int(month) == 2:
                day = 1
                month = int(month) + 1
            if int(month) >= 12:
                month = 1
                year = int(year) + 1
            minute = self.normalize_day(str(minute)) #Function
            hour = self.normalize_day(str(hour)) #Function
            day = self.normalize_day(str(day)) #Function
            month = self.normalize_day(str(month)) #Function
            endtime = str(year) + str(month) + str(day) + str(hour) + str(minute) + str(sec)
            self.cursor.execute("UPDATE 1_peng_status SET status='" + str(endtime) + "' WHERE name='endtime'")
        
    def peng_start(self, time, date):
        global info_pm, pkup_go_admin, sentto, peng_url
        sentto = 0
        self.cursor.execute("SELECT status FROM 1_peng_status WHERE name='game'")
        game_started = self.cursor.fetchone()
        game_started = game_started[0]

        self.cursor.execute("SELECT status FROM 1_peng_status WHERE name='players'")
        players = self.cursor.fetchone()
        players = players[0]
        if players == "10" and game_started == "0":
            self.cursor.execute("UPDATE 1_peng_status SET status='1' WHERE name='game'")
            self.peng_endtime(time, date) #Function
            #PASSWORD#
            password = random.randint(100000, 999999)
            self.cursor.execute("UPDATE 1_peng_status SET status='" + str(password) + "' WHERE name='password'")
            #VOTES#
            self.cursor.execute("SELECT map FROM 1_peng_map ORDER BY vote DESC")
            votes = self.cursor.fetchone()
            smap = str(votes[0])
            self.cursor.execute("SELECT mode FROM 1_peng_mode ORDER BY vote DESC")
            votes = self.cursor.fetchone()
            stype = str(votes[0])
            #CAPTAIN#
            captain1 = random.randint(0, 9)
            self.cursor.execute("UPDATE 1_peng_player SET captain='1' WHERE id='" + str(captain1) + "'")
            captain2 = random.randint(0, 9)
            while(captain1 == captain2):
                captain2 = random.randint(0, 9)
            self.cursor.execute("UPDATE 1_peng_player SET captain='1' WHERE id='" + str(captain2) + "'")
            self.cursor.execute("SELECT name FROM 1_peng_player WHERE captain='1'")
            capnick = self.cursor.fetchall()
            capnick1 = capnick[0][0]
            capnick2 = capnick[1][0]
            #SERVER SET#
            data = peng_url + "exec " + str(stype)
            urllib.urlopen(data)
            sleep(1)
            data = peng_url + 'sv_joinmessage\" Captains: ' + capnick1 + ' ' + capnick2
            urllib.urlopen(data)
            sleep(1)
            data = peng_url + "g_password " + str(password)
            urllib.urlopen(data)
            sleep(1)
            data = peng_url + "map " + str(smap)
            urllib.urlopen(data)
            msg = pkup_go_admin.replace(".captain1.", capnick1)
            msg = msg.replace(".captain2.", capnick2)
            msg = msg.replace(".type.", stype)
            msg = msg.replace(".password.", str(password))
            msg = msg.replace(".map.", smap)
            self.s.send('PRIVMSG ' + priv_chan + ' :' + msg + '\n')
            self.s.send('PRIVMSG ' + priv_chan + ' :' + info_pm + '\n')
        
            self.cursor.execute("SELECT name,qauth FROM 1_peng_player WHERE id='1'")
            player1 = self.cursor.fetchone()
            self.cursor.execute("SELECT name,qauth FROM 1_peng_player WHERE id='2'")
            player2 = self.cursor.fetchone()
            self.cursor.execute("SELECT name,qauth FROM 1_peng_player WHERE id='3'")
            player3 = self.cursor.fetchone()
            self.cursor.execute("SELECT name,qauth FROM 1_peng_player WHERE id='4'")
            player4 = self.cursor.fetchone()
            self.cursor.execute("SELECT name,qauth FROM 1_peng_player WHERE id='5'")
            player5 = self.cursor.fetchone()
            self.cursor.execute("SELECT name,qauth FROM 1_peng_player WHERE id='6'")
            player6 = self.cursor.fetchone()
            self.cursor.execute("SELECT name,qauth FROM 1_peng_player WHERE id='7'")
            player7 = self.cursor.fetchone()
            self.cursor.execute("SELECT name,qauth FROM 1_peng_player WHERE id='8'")
            player8 = self.cursor.fetchone()
            self.cursor.execute("SELECT name,qauth FROM 1_peng_player WHERE id='9'")
            player9 = self.cursor.fetchone()
            self.cursor.execute("SELECT name,qauth FROM 1_peng_player WHERE id='0'")
            player10 = self.cursor.fetchone()
            self.cursor.execute("INSERT INTO `1_peng_stats` (`Map`, `Type`, `Player1`, `qauth1`, `Player2`, `qauth2`, `Player3`, `qauth3`, `Player4`, `qauth4`, `Player5`, `qauth5`, `Player6`, `qauth6`, `Player7`, `qauth7`, `Player8`, `qauth8`, `Player9`, `qauth9`, `Player10`, `qauth10`, `captain1`, `Captain2`, `Time`, `Ending`) VALUES ('" + str(smap) + "', '" + str(stype) + "', '" + str(player1[0]) + "', '" + str(player1[1]) + "', '" + str(player2[0]) + "', '" + str(player2[1]) + "', '" + str(player3[0]) + "', '" + str(player3[1]) + "', '" + str(player4[0]) + "', '" + str(player4[1]) + "', '" + str(player5[0]) + "', '" + str(player5[1]) + "', '" + str(player6[0]) + "', '" + str(player6[1]) + "', '" + str(player7[0]) + "', '" + str(player7[1]) + "', '" + str(player8[0]) + "', '" + str(player8[1]) + "', '" + str(player9[0]) + "', '" + str(player9[1]) + "', '" + str(player10[0]) + "', '" + str(player10[1]) + "', '" + str(capnick1) + "', '" + str(capnick2) + "', '" + str(self.getdate) + " " + str(self.gettime) + "', 'playing' )")
    
    def peng_end(self, time, date):
        self.cursor.execute("SELECT status FROM 1_peng_status WHERE name='game'")
        game_started = self.cursor.fetchone()
        game_started = game_started[0]
        self.cursor.execute("SELECT status FROM 1_peng_status WHERE name='endtime'")
        pengend = self.cursor.fetchone()
        pengend = pengend[0]
        date = date.split('.')
        time = time.replace(':', '')
        newdate = date[2] + date[1] + date[0] + time
        if newdate >= pengend and game_started == "1":
            self.cursor.execute("SELECT ID FROM 1_peng_stats ORDER BY ID DESC")
            ending = self.cursor.fetchone()
            self.cursor.execute("UPDATE 1_peng_stats SET ending='normal' WHERE ID='" + str(ending[0]) + "'")
            self.peng_reset()

    def peng_gameover(self):
        self.cursor.execute("SELECT status FROM 1_peng_status WHERE name='gameover'")
        gameover = self.cursor.fetchone()
        gameover = gameover[0]
        if int(gameover) == 0:
            self.cursor.execute("SELECT ID FROM 1_peng_stats ORDER BY ID DESC")
            ending = self.cursor.fetchone()
            self.cursor.execute("UPDATE 1_peng_stats SET ending='gameover' WHERE ID='" + str(ending[0]) + "'")
            self.peng_reset()

    def peng_reset(self):
        #PLAYERS
        self.cursor.execute("SELECT id FROM 1_peng_player ORDER BY id")
        players = self.cursor.fetchall()
        num = 0
        while(num < len(players)):
            self.cursor.execute("UPDATE 1_peng_player SET name='' WHERE id='" + str(players[num][0]) + "'")
            self.cursor.execute("UPDATE 1_peng_player SET qauth='' WHERE id='" + str(players[num][0]) + "'")
            self.cursor.execute("UPDATE 1_peng_player SET map='0' WHERE id='" + str(players[num][0]) + "'")
            self.cursor.execute("UPDATE 1_peng_player SET mode='0' WHERE id='" + str(players[num][0]) + "'")
            self.cursor.execute("UPDATE 1_peng_player SET captain='0' WHERE id='" + str(players[num][0]) + "'")
            self.cursor.execute("UPDATE 1_peng_player SET botid='' WHERE id='" + str(players[num][0]) + "'")
            self.cursor.execute("UPDATE 1_peng_player SET gameover='' WHERE id='" + str(players[num][0]) + "'")
            num = num + 1
        #STATUS#
        self.cursor.execute("UPDATE 1_peng_status SET status='0' WHERE name='game'")
        self.cursor.execute("UPDATE 1_peng_status SET status='4' WHERE name='gameover'")
        self.cursor.execute("UPDATE 1_peng_status SET status='0' WHERE name='players'")
        #MAPS#
        self.cursor.execute("SELECT id FROM 1_peng_map ORDER BY id")
        maps = self.cursor.fetchall()
        map_check = str(maps)
        if map_check != '()':
            num = 0
            while(num < len(maps)):
                self.cursor.execute("UPDATE 1_peng_map SET vote='0' WHERE id='" + str(maps[num][0]) + "'")
                num = num + 1
        #MODES#
        self.cursor.execute("SELECT id FROM 1_peng_mode ORDER BY id")
        modes = self.cursor.fetchall()
        mode_check = str(modes)
        if mode_check != '()':
            num = 0
            while(num < len(modes)):
                self.cursor.execute("UPDATE 1_peng_mode SET vote='0' WHERE id='" + str(modes[num][0]) + "'")
                num = num + 1
        #MSG#
            self.s.send('PRIVMSG ' + priv_chan + ' :' + info_signup + '\n')
    
    def run(self):
        #self.s.setsockopt(socket.SOL_SOCKET,IN.SO_BINDTODEVICE,struct.pack("%ds" % (len("eth0.1")+1,), "eth0.1"))
        self.s.bind(("178.79.142.114",0))
        self.s.connect((self.host, self.port))
        self.s.send("NICK %s\r\n" % self.nick)
        self.s.send("USER %s 0 0 %s\r\n" % (self.identt, self.realname))
        
        stop = 0
        sentto = 0

        while True:
            if self.useprint:
                try:
                    irctext = self.s.recv(4096).split('\n')
                    textcounter = 0
                    print irctext
                    while(textcounter < len(irctext)):

                        text = irctext[textcounter]
                        if len(text) > 0:
                            print self.nick + text
                        data = text.split()
                        textcounter = textcounter + 1
                        if len(data) <= 1:
                            data = ['', '']
                            
                        getall = ctime()
                        getall = getall.split()
                        getday = getall[2]
                        getday = self.normalize_day(getday) # Function
                        getmonth = getall[1]
                        getmonth = getmonth.replace("Jan", "01")
                        getmonth = getmonth.replace("Feb", "02")
                        getmonth = getmonth.replace("Mar", "03")
                        getmonth = getmonth.replace("Apr", "04")
                        getmonth = getmonth.replace("May", "05")
                        getmonth = getmonth.replace("Jun", "06")
                        getmonth = getmonth.replace("Jul", "07")
                        getmonth = getmonth.replace("Aug", "08")
                        getmonth = getmonth.replace("Sep", "09")
                        getmonth = getmonth.replace("Oct", "10")
                        getmonth = getmonth.replace("Nov", "11")
                        getmonth = getmonth.replace("Dec", "12")
                        getdate = getday + "." + getmonth + "." + getall[4]
                        gettime = getall[3]
                        sgettime = gettime.split(":")
                        gettime = sgettime[0] + ":" + sgettime[1] + ":" + sgettime[2]
            
                        if data[1] == "513" and len(data) >= 9:
                            self.s.send('PONG ' + data[8] + '\n')
                        if "PING" in text and len(data) >= 2:
                            self.s.send('PONG ' + data[1] + '\n')
                        if "Nickname is already in use." in text:
                            self.s.send('NICK pengMaster1 \r\n')
                        if "Message of the Day" in text:
                            self.s.send ( 'PRIVMSG Q@CServe.quakenet.org :AUTH pengbotMaster hk-T7nEtdK\n')
                            sleep(2)
                            #self.s.send ('MODE %s :+x \r\n' % (self.nick))
                            self.s.send("JOIN %s \r\n" % (priv_chan))
                            self.s.send("JOIN %s \r\n" % (pub_chan))
                            self.s.send("JOIN %s \r\n" % (admin_chan))  

                        #AUTODELETE#
                        self.auto_delete(gettime,getdate) #Function
        
                        #BLOCKED#
                        self.auto_blocked(gettime,getdate) #Function
        
                        #REQUEST#
                        self.requeststatus() #Function
        
                        #PICKUP#
                        self.peng_start(gettime,getdate) #Function
                        self.peng_end(gettime,getdate) #Function
                        self.peng_gameover() #Function    
                        
                        if data[1] == "JOIN" and len(data) >= 3:
                            getnick = data[0].split("!")
                            nick = getnick[0].replace(":","")
                            channel = data[2]
                            if channel == priv_chan:
                                if 'pengbot' in nick:
                                    sleep(0.5)
                                    self.s.send('PRIVMSG ' + priv_chan + ' :' + sup_join + ' ' + nick + '\n')
                                    nick = nick.replace('pengbot','')
                                    self.cursor.execute("UPDATE 1_peng_online SET status='online' WHERE bot='" + nick + "'")
            
                        if data[1] == "QUIT" and len(data) >= 3:
                            getnick = data[0].split("!")
                            nick = getnick[0].replace(":","")
                            channel = data[2]
                            if 'pengbot' in nick:
                                nick = nick.replace('pengbot','')
                                self.cursor.execute("UPDATE 1_peng_online SET status='offline' WHERE bot='" + nick + "'")
                                print nick
                                sleep(2)
                                threads[nick] = botPeng(nick,1)
                                if not threads[nick].isAlive():
                                    threads[nick].start()
                                self.s.send('PRIVMSG ' + priv_chan + ' :restarting: ' + nick + '\n')
            
                        if data[1] == "353" and len(data) >= 5:
                            if data[4] == priv_chan:
                                replacer = data[0] + " " + data[1] + " " + data[2] + " " + data[3] + " " + data[4] + " :"
                                getnames = text.replace(replacer, "")
                                getnames = getnames.split()
                                zahl = 0
                                while(zahl < len(getnames)):
                                    if "pengbot" in getnames[zahl]:
                                        getnames[zahl] = getnames[zahl].replace("pengbot","")
                                        getnames[zahl] = getnames[zahl].replace("+","")
                                        getnames[zahl] = getnames[zahl].replace("@","")
                                        self.cursor.execute("UPDATE 1_peng_online SET status='online' WHERE bot='" + getnames[zahl] + "'")
                                    zahl = zahl + 1
                                
                            
                        if "PRIVMSG" in text and len(data) >= 4:
                            getnick = data[0].split("!")
                            nick = getnick[0].replace(":","")
                            nick = nick.replace("\'","`")
                            
                            if data[3] == ":!quit":
                                host = getnick[1]
                                print data[3] + " " + host
                                if host in OWNER:
                                    self.s.send('QUIT\n')
                                    self.s.close()
                                    sys.exit()

			    if data[3] == ":!myport":
				self.s.send('PRIVMSG ' + priv_chan + ' :' + str(self.port) + '\n')
            
                            if data[3] == ":!newthread":
                                channel = data[2]
                                if channel == priv_chan or channel == admin_chan:
                                    if len(data) == 5:
                                        number = data[4]
                                        threads[number] = botPeng(number,1)
                                        if not threads[number].isAlive():    
                                            threads[number].start()
                                    else:
                                        self.s.send('PRIVMSG ' + priv_chan + ' :' + cmd_prefix + 'newthread <number>\n')  
                                        
                            if data[3] == ":!startbots":
                                channel = data[2]
                                if channel == priv_chan or channel == admin_chan:
                                    if len(data) == 5:
                                        number = data[4]
                                        for i in range(1,int(number)):
                                            if len(str(i)) == 1:
                                                currentnum = "00" + str(i)
                                            else:
                                                currentnum = "0" + str(i)
 
                                            threads[currentnum] = botPeng(currentnum,1)
                                            threads[currentnum].start()

                            if data[3] == ":!startbotss":
                                channel = data[2]
                                if channel == priv_chan or channel == admin_chan:
                                    if len(data) == 5:
                                        number = data[4]
                                        for i in range(17,int(number)):
                                            if len(str(i)) == 1:
                                                currentnum = "00" + str(i)
                                            else:
                                                currentnum = "0" + str(i)
 
                                            threads[currentnum] = botPeng(currentnum,1)
                                            threads[currentnum].start()									

                            if data[3] == (":" + bot_new):
                                channel = data[2]
                                if channel == priv_chan:
                                    if len(data) == 6:
                                        if data[4] == "RINGER":
                                            self.s.send('PRIVMSG ' + priv_chan + ' :' + sup_spam + ' RINGER ' + data[5] + '\n')
                                        if data[4] == "PCW":
                                            self.s.send('PRIVMSG ' + priv_chan + ' :' + sup_spam + ' PCW ' + data[5] + '\n')
                                        if data[4] == "CW":
                                            self.s.send('PRIVMSG ' + priv_chan + ' :' + sup_spam + ' CW ' + data[5] + '\n')
                                        if data[4] == "MSG":
                                            self.s.send('PRIVMSG ' + priv_chan + ' :' + sup_spam + ' MSG ' + data[5] + '\n')
                                        if data[4] == "RECRUIT":
                                            self.s.send('PRIVMSG ' + priv_chan + ' :' + sup_spam + ' RECRUIT ' + data[5] + '\n')
                                        if data[4] == "GTV":
                                            self.s.send('PRIVMSG ' + priv_chan + ' :' + sup_spam + ' GTV ' + data[5] + '\n')
            
                            if data[3] == (":" + info_sentto):
                                channel = data[2]
                                if channel == priv_chan:
                                    if sentto == 0:
                                        sentto = 1
                                        self.s.send('PRIVMSG ' + priv_chan + ' :' + info_datasent + '\n')
                                            
                            if data[3] == (":" + cmd_prefix + pickup_prefix):
                                channel = data[2]
                                if channel == priv_chan:
                                    if len(data) > 4:
                                        if data[4] == pickup_lock:
                                            self.cursor.execute("UPDATE 1_peng_status SET status='1' WHERE name='lock'")
                                            self.s.send('PRIVMSG ' + priv_chan + ' :[PICKUP] LOCKED.\n')
                                        elif data[4] == pickup_unlock:
                                            self.cursor.execute("UPDATE 1_peng_status SET status='0' WHERE name='lock'")
                                            self.s.send('PRIVMSG ' + priv_chan + ' :[PICKUP] UNLOCKED.\n')
                                        elif data[4] == pickup_reset:
                                            self.peng_reset() #Function
                                        elif data[4] == pickup_getdata:
                                            self.cursor.execute("SELECT status FROM 1_peng_status WHERE name='server'")
                                            server = self.cursor.fetchone()
                                            server = server[0]
                                            self.cursor.execute("SELECT status FROM 1_peng_status WHERE name='password'")
                                            password = self.cursor.fetchone()
                                            password = password[0]
                                            msg = pkup_pw.replace(".server.", server)
                                            msg = msg.replace(".password.", password)
                                            self.s.send('PRIVMSG ' + nick + ' :' + msg + '\n')
                                        elif data[4] == pickup_addmap and len(data) == 6:
                                            self.cursor.execute("INSERT INTO 1_peng_map (map, vote) VALUES ('" + data[5] + "','0')")
                                            self.s.send('PRIVMSG ' + priv_chan + ' :[PICKUP] Map ' + data[5] + ' added.\n')
                                        elif data[4] == pickup_delmap and len(data) == 6:
                                            self.cursor.execute("DELETE from 1_peng_map WHERE map=%s", (data[5]))
                                            self.s.send('PRIVMSG ' + priv_chan + ' :[PICKUP] Map ' + data[5] + ' deleted.\n')
                                        elif data[4] == pickup_addmode and len(data) == 6:
                                            self.cursor.execute("INSERT INTO 1_peng_mode (mode, vote) VALUES ('" + data[5] + "','0')")
                                            self.s.send('PRIVMSG ' + priv_chan + ' :[PICKUP] Mode ' + data[5] + ' added.\n')
                                        elif data[4] == pickup_delmode and len(data) == 6:
                                            self.cursor.execute("DELETE from 1_peng_mode WHERE mode=%s", (data[5]))
                                            self.s.send('PRIVMSG ' + priv_chan + ' :[PICKUP] Mode ' + data[5] + ' deleted.\n')
                                        elif data[4] == pickup_test and len(data) == 6:
                                            self.cursor.execute("UPDATE 1_peng_status SET status='" + data[5] + "' WHERE name='players'")
                                            self.s.send('PRIVMSG ' + priv_chan + ' :[PICKUP] Players set to ' + data[5] + '.\n')
                                        elif data[4] == pickup_server and len(data) == 6:
                                            self.cursor.execute("UPDATE 1_peng_status SET status='" + data[5] + "' WHERE name='server'")
                                            self.s.send('PRIVMSG ' + priv_chan + ' :[PICKUP] Server changed to ' + data[5] + '\n')
            
                            if data[3] == (":" + cmd_prefix + bot_add):
                                channel = data[2]
                                if channel == priv_chan:
                                    if len(data) == 5:
                                        if data[4].isdigit():
                                            number = data[4]
                                            self.cursor.execute("INSERT INTO 1_peng_channels (id, number) VALUES ('" + number + "', '0')")
                                            self.cursor.execute("INSERT INTO 1_peng_online (bot,status) VALUES ('" + number + "', '')")
                                            self.s.send('WHOIS pengbot' + number + '\n')
                                            self.s.send('PRIVMSG Q :chanlev ' + priv_chan + ' #pengbot' + number + ' +v\n')
                                            self.s.send('PRIVMSG Q :chanlev ' + pub_chan + ' #pengbot' + number + ' +v\n')
                                            self.s.send('PRIVMSG ' + priv_chan + ' :pengbot' + number + ' successfully added.\n')
                                        else:
                                            self.s.send('PRIVMSG ' + priv_chan + ' :' + cmd_prefix + bot_add + ' <number>\n')
                                    else:
                                        self.s.send('PRIVMSG ' + priv_chan + ' :' + cmd_prefix + bot_add + ' <number>\n')
            
                            if data[3] == (":" + cmd_prefix + bot_delete):
                                channel = data[2]
                                if channel == priv_chan:
                                    if len(data) == 5:
                                        if data[4].isdigit():
                                            number = data[4]
                                            self.cursor.execute("DELETE from 1_peng_bots WHERE id='" + number + "'")
                                            self.cursor.execute("DELETE from 1_peng_channels WHERE id='" + number + "'")
                                            self.cursor.execute("DELETE from 1_peng_online WHERE id='" + number + "'")
                                            self.s.send('PRIVMSG ' + priv_chan + ' :pengbot' + number + ' successfully deleted.\n')
                                        else:
                                            self.s.send('PRIVMSG ' + priv_chan + ' :' + cmd_prefix + bot_delete + ' <number>\n')
                                    else:
                                        self.s.send('PRIVMSG ' + priv_chan + ' :' + cmd_prefix + bot_delete + ' <number>\n')
            
                            if data[3] == (":" + cmd_prefix + ban_add):
                                channel = data[2]
                                if channel == priv_chan or channel == admin_chan:
                                    if len(data) >= 6:
                                        auth = data[4]
                                        reason = self.text_addinfo(data,5)
                                        self.cursor.execute("INSERT INTO 1_peng_ban (`Auth`, `Reason`) VALUES (%s, %s)", (auth, reason))
                                        self.s.send('PRIVMSG ' + channel + ' :Ban of ' + auth + ' was successfully added.\n')
                                    else:
                                        self.s.send('PRIVMSG ' + channel + ' :' + cmd_prefix + ban_add + ' <authnick> <reason>\n')
            
                            if data[3] == (":" + cmd_prefix + ban_delete):
                                channel = data[2]
                                if channel == priv_chan or channel == admin_chan:
                                    if len(data) == 5:
                                        auth = data[4]
                                        self.cursor.execute("SELECT * FROM 1_peng_ban WHERE Auth=%s", (auth))
                                        banavi = self.cursor.fetchone()
                                        if banavi != None:
                                            self.cursor.execute("DELETE from 1_peng_ban WHERE Auth=%s", (auth))
                                            self.s.send('PRIVMSG ' + channel + ' :Ban of ' + auth + ' was successfully deleted.\n')
                                        else:
                                            self.s.send('PRIVMSG ' + channel + ' :' + auth + ' isn\'t banned.\n')
                                    else:
                                        self.s.send('PRIVMSG ' + channel + ' :' + cmd_prefix + ban_delete + ' <authnick>\n')
            
                            if data[3] == (":" + cmd_prefix + cmd_log):
                                channel = data[2]
                                if channel == priv_chan:
                                    if len(data) == 6:
                                        if data[5].isdigit() == True:
                                            self.cursor.execute("SELECT id,type,channel,nick,number,message,date,time FROM 1_peng_messages WHERE auth=%s ORDER BY id DESC", (data[4]))
                                            log = self.cursor.fetchall()
                                            num = 0
                                            stop = 0
                                            while(stop < 1):
                                                if num < (int(data[5])) and num < len(log):
                                                    log1 = log[num]
                                                    logid = log1[0]
                                                    logtype = log1[1]
                                                    logchan = log1[2]
                                                    lognick = log1[3]
                                                    lognum = log1[4]
                                                    logmsg = log1[5]
                                                    logdate = log1[6]
                                                    logtime = log1[7]
                                                    if logtype != 'msg' or logtype != 'amsg' or logtype != 'gtv':
                                                        alogmsg = '[LOG] ' + str(logchan) + ' - ' + str(lognick) + ' - ' + str(data[4]) + ' - !' + str(logtype) + ' ' + str(lognum) + ' ' + str(logmsg) + ' - ' + str(logdate) + ' ' + str(logtime)
                                                    else:
                                                        alogmsg = '[LOG] ' + str(logchan) + ' - ' + str(lognick) + ' - ' + str(data[4]) + ' - !' + str(logtype) + ' ' + str(logmsg) + ' - ' + str(logdate) + ' ' + str(logtime)
                                                    self.s.send('PRIVMSG ' + priv_chan + ' :' + alogmsg + '\n')
                                                    sleep(2)
                                                else:
                                                    stop = 1
                                                num = num + 1
                                        else:
                                            self.s.send('PRIVMSG ' + priv_chan + ' :' + cmd_prefix + cmd_log + ' <auth> <number>\n')
                                    else:
                                        self.s.send('PRIVMSG ' + priv_chan + ' :' + cmd_prefix + cmd_log + ' <auth> <number>\n')
                 
            
                            if data[3] == (":" + cmd_prefix + q_list):
                                channel = data[2]
                                if channel == priv_chan or channel == admin_chan:
                                    if len(data) == 4:
                                        self.cursor.execute("SELECT id,channel,channeltype,qauth,email,clan,homepage FROM 1_peng_requests WHERE handle='0'")
                                        req = self.cursor.fetchall()
                                        if len(req) > 0:
                                            num = 0
                                            stop = 0
                                            while(stop < 1):
                                                if num < len(req):
                                                    req1 = req[num]
                                                    reqid = req1[0]
                                                    reqchan = req1[1]
                                                    reqtype = req1[2]
                                                    reqauth = req1[3]
                                                    reqmail = req1[4]
                                                    reqclan = req1[5]
                                                    reqpage = req1[6]
                                                    if reqchan[0] != "#":
                                                        self.cursor.execute("UPDATE 1_peng_requests SET channel='#" + str(reqchan) + "' WHERE id='" + str(reqid) + "'")
                                                        reqmsg = 'REQUEST ' + str(reqid) + ': #' + str(reqchan) + ' as ' + str(reqtype) + ' by ' + str(reqauth) + ' (mailto:' + str(reqmail) + ')'
                                                    reqmsg = 'REQUEST ' + str(reqid) + ': ' + str(reqchan) + ' as ' + str(reqtype) + ' by ' + str(reqauth) + ' (mailto:' + str(reqmail) + ')'
                                                    if reqpage != '':
                                                        reqmsg = reqmsg + " | Page: " + reqpage
                                                    if reqclan != '':
                                                        reqmsg = reqmsg + " | Clan: " + reqclan
                                                    self.s.send('PRIVMSG ' + channel + ' :' + reqmsg + '\n')
                                                    sleep(2)
                                                else:
                                                    stop = 1
                                                num = num + 1
                                        else:
                                            self.s.send('PRIVMSG ' + channel + ' :No new requests\n')
                                    else:
                                        self.s.send('PRIVMSG ' + channel + ' :' + cmd_prefix + q_list + '\n')
                                        
                            if data[3] == (":" + cmd_prefix + q_accept):
                                channel = data[2]
                                if channel == priv_chan or channel == admin_chan:
                                    if len(data) == 5:
                                        self.cursor.execute("SELECT channel,id FROM 1_peng_requests WHERE id='" + data[4] + "'")
                                        req = self.cursor.fetchone()
                                        if len(req) != None:
                                            self.cursor.execute("SELECT * FROM 1_peng_channels ORDER BY id")
                                            peng = self.cursor.fetchall()
                                            stop = 0
                                            num = 0
                                            while(stop < 1):
                                                if num < len(peng):
                                                    peng1 = peng[num]
                                                    if int(peng1[1]) < 10:
                                                        sstop = 0
                                                        number = 2
                                                        while(sstop < 1):
                                                            if number <= 11:
                                                                if peng1[number] == '':
                                                                    #put chan into this
                                                                    self.cursor.execute("UPDATE 1_peng_channels SET number='" + str(int(peng1[1]) + 1) + "' WHERE id='" + peng1[0] + "'")
                                                                    self.cursor.execute("UPDATE 1_peng_channels SET chan" + str(int(number - 1)) + "='" + str(req[0]) + "' WHERE id='" + str(peng1[0]) + "'")
                                                                    #add chan into botnick (peng1[0])
                                                                    self.cursor.execute("INSERT INTO 1_peng_bots (`id`, `channel`, `pcw`, `cw`, `ringer`, `msg`, `ablemsg`, `amsg`, `recruit`, `gtv`, `ablegtv`,`pickup`) VALUES ('" + peng1[0] + "', '" + req[0] + "', 'on', 'on', 'on', 'on', 'off', 'on', 'on', 'on', 'off', 'on')")
                                                                    self.s.send('PRIVMSG ' + priv_chan + ' :' + sup_join + ' pengbot' + peng1[0] + ' ' + str(req[0]) + '\n')
                                                                    self.cursor.execute("UPDATE 1_peng_requests SET handle='1' WHERE id='" + str(req[1]) + "'")
                                                                    self.s.send('PRIVMSG ' + channel + ' :Request accepted.\n')
                                                                    sstop = 1
                                                                    stop = 1
                                                            else:
                                                                sstop = 1
                                                            number = number + 1
                                                else:
                                                    stop = 1
                                                    self.s.send('PRIVMSG ' + channel + ' :Channel limit reached for all bots. Add a new bot to continue.\n')
                                                num = num + 1
                                        else:
                                            self.s.send('PRIVMSG ' + channel + ' :Wrong id: ' + cmd_prefix + q_accept + ' <id>\n')
                                    else:
                                        self.s.send('PRIVMSG ' + channel + ' :' + cmd_prefix + q_accept + ' <id>\n')
                                        
                            if data[3] == (":" + cmd_prefix + q_refuse):
                                channel = data[2]
                                if channel == priv_chan or channel == admin_chan:
                                    if len(data) >= 5:
                                        self.cursor.execute("SELECT email,id,qauth,channel FROM 1_peng_requests WHERE id='" + data[4] + "'")
                                        req = self.cursor.fetchone()
                                        if len(req) > 0:
                                            reqmail = req[0]
                                            reqauth = req[2]
                                            reqchan = req[3]
                                            reason = ''
                                            if len(data) > 5:
                                                reason = self.text_addinfo(data,5)
                                            else:
                                                reason = "Your request doesnt fit with our rules. Read the rules and try later again."
                                            address = str(url) + "?email=" + str(reqmail) + "&qauth=" + str(reqauth) + "&channel=" + str(reqchan) + "&handle=" + str(nick) + "&reason=" + str(reason)
                                            urllib2.urlopen(address)
                                            self.cursor.execute("UPDATE 1_peng_requests SET handle='1' WHERE id='" + str(req[1]) + "'")
                                            self.s.send('PRIVMSG ' + channel + ' :Request refused.\n')
                                            
                                        else:
                                            self.s.send('PRIVMSG ' + channel + ' :Wrong id: ' + cmd_prefix + q_refuse + ' <id> </reason/>\n')
                                    else:
                                        self.s.send('PRIVMSG ' + channel + ' :' + cmd_prefix + q_refuse + ' <id> </reason/>\n')
                                        
                            if data[3] == (":" + cmd_prefix + q_del):
                                channel = data[2]
                                if channel == priv_chan or channel == admin_chan:
                                    if len(data) >= 5:
                                        self.cursor.execute("SELECT id FROM 1_peng_requests WHERE id='" + data[4] + "'")
                                        req = self.cursor.fetchone()
                                        if len(req) > 0:
                                            self.cursor.execute("UPDATE 1_peng_requests SET handle='1' WHERE id='" + str(req[0]) + "'")
                                            self.s.send('PRIVMSG ' + channel + ' :Request deleted.\n')
                                            
                                        else:
                                            self.s.send('PRIVMSG ' + channel + ' :Wrong id: ' + cmd_prefix + q_refuse + ' <id> </reason/>\n')
                                    else:
                                        self.s.send('PRIVMSG ' + channel + ' :' + cmd_prefix + q_refuse + ' <id> </reason/>\n')
                                        
                            if data[3] == (":" + cmd_prefix + q_refuseall):
                                channel = data[2]
                                if channel == priv_chan or channel == admin_chan:
                                    if len(data) == 4:
                                        self.cursor.execute("SELECT email,id,qauth,channel FROM 1_peng_requests WHERE handle='0'")
                                        req = self.cursor.fetchall()
                                        numb = 0
                                        stop = 0
                                        while(stop < 1):
                                            if numb < len(req):
                                                reqmail = req[numb][0]
                                                reqauth = req[numb][2]
                                                reqchan = req[numb][3]
                                                reason = "Your request doesnt fit with our rules. Read the rules and try later again."
                                                address = str(url) + "?email=" + str(reqmail) + "&qauth=" + str(reqauth) + "&channel=" + str(reqchan) + "&handle=" + str(nick) + "&reason=" + str(reason)
                                                #urllib2.urlopen(address)
                                                self.cursor.execute("UPDATE 1_peng_requests SET handle='1' WHERE id='" + str(req[numb][1]) + "'")
                                                sleep(2)
                                            else:
                                                stop = 1
                                            numb = numb + 1
                                        self.s.send('PRIVMSG ' + channel + ' :All request refused.\n')
                                    else:
                                        self.s.send('PRIVMSG ' + channel + ' :' + cmd_prefix + q_refuseall + '\n')
            
                                        
                            if data[3] == (":" + cmd_prefix + chan_add):
                                channel = data[2]
                                if channel == priv_chan:
                                    if len(data) == 5:
                                        if "#" in data[4]:
                                            self.cursor.execute("SELECT * FROM 1_peng_channels ORDER BY id")
                                            peng = self.cursor.fetchall()
                                            stop = 0
                                            num = 0
                                            while(stop < 1):
                                                if num < len(peng):
                                                    peng1 = peng[num]
                                                    if int(peng1[1]) < 10:
                                                        sstop = 0
                                                        number = 2
                                                        while(sstop < 1):
                                                            if number <= 11:
                                                                if peng1[number] == '':
                                                                    #put chan into this
                                                                    self.cursor.execute("UPDATE 1_peng_channels SET number='" + str(int(peng1[1]) + 1) + "' WHERE id='" + peng1[0] + "'")
                                                                    self.cursor.execute("UPDATE 1_peng_channels SET chan" + str(int(number - 1)) + "='" + str(data[4]) + "' WHERE id='" + str(peng1[0]) + "'")
                                                                    #add chan into botnick (peng1[0])
                                                                    self.cursor.execute("INSERT INTO 1_peng_bots (`id`, `channel`, `pcw`, `cw`, `ringer`, `msg`, `ablemsg`, `amsg`, `recruit`, `gtv`, `ablegtv`,`pickup`) VALUES ('" + peng1[0] + "', '" + data[4] + "', 'on', 'on', 'on', 'on', 'off', 'on', 'on', 'on', 'off', 'on')")
                                                                    self.s.send('PRIVMSG ' + priv_chan + ' :' + sup_join + ' pengbot' + peng1[0] + ' ' + data[4] + '\n')
                                                                    sstop = 1
                                                                    stop = 1
                                                            else:
                                                                sstop = 1
                                                            number = number + 1
                                                else:
                                                    stop = 1
                                                    self.s.send('PRIVMSG ' + priv_chan + ' :Channel limit reached for all bots. Add a new bot to continue.\n')
                                                num = num + 1
                                        else:
                                            self.s.send('PRIVMSG ' + priv_chan + ' :Channel missing: ' + cmd_prefix + chan_add + ' <#channel>\n')
                                    else:
                                        self.s.send('PRIVMSG ' + priv_chan + ' :Not enough parameter: ' + cmd_prefix + chan_add + ' <#channel>\n')
            
                            if data[3] == (":" + cmd_prefix + chan_remove):
                                channel = data[2]
                                if channel == priv_chan:
                                    if len(data) == 5:
                                        if "#" in data[4]:
                                            self.cursor.execute("SELECT id FROM 1_peng_bots WHERE channel='" + data[4] + "'")
                                            peng = self.cursor.fetchone()
                                            if not peng == None:
                                                self.cursor.execute("SELECT * FROM 1_peng_channels WHERE id='" + peng[0] + "'")
                                                chanlist = self.cursor.fetchone()
                                                stop = 0
                                                sstop = 0
                                                number = 2
                                                while(sstop < 1):
                                                    if number <= 11:
                                                        if chanlist[number] == data[4]:
                                                            #put chan into this
                                                            self.cursor.execute("UPDATE 1_peng_channels SET number='" + str(int(chanlist[1]) - 1) + "' WHERE id='" + str(peng[0]) + "'")
                                                            self.cursor.execute("UPDATE 1_peng_channels SET chan" + str(int(number - 1)) + "='' WHERE id='" + str(peng[0]) + "'")
                                                            #remove chan from botnick (peng1[0])
                                                            self.cursor.execute("DELETE from 1_peng_bots WHERE id='" + peng[0] + "' AND channel='" + data[4] + "'")
                                                            self.s.send('PRIVMSG ' + priv_chan + ' :' + sup_remove + ' pengbot' + peng[0] + ' ' + data[4] + '\n')
                                                    else:
                                                        sstop = 1
                                                    number = number + 1
                                            else:
                                                self.s.send('PRIVMSG ' + priv_chan + ' :Channel isn\'t added: ' + cmd_prefix + chan_remove + ' <#channel>\n')
                                        else:
                                            self.s.send('PRIVMSG ' + priv_chan + ' :Channel missing: ' + cmd_prefix + chan_remove + ' <#channel>\n')
                                    else:
                                        self.s.send('PRIVMSG ' + priv_chan + ' :Not enough parameter: ' + cmd_prefix + chan_remove + ' <#channel>\n')
            
                            if data[3] == (":" + cmd_prefix + msg_enable):
                                channel = data[2]
                                if channel == priv_chan:
                                    if len(data) == 5:
                                        if "#" in data[4]:
                                            self.cursor.execute("UPDATE 1_peng_bots SET ablemsg='on' WHERE channel='" + data[4] + "'")
                                            self.s.send('PRIVMSG ' + priv_chan + ' :#ENABLED#\n')
                                        else:
                                            self.s.send('PRIVMSG ' + priv_chan + ' :Channel missing: ' + cmd_prefix + msg_enable + ' <#channel>\n')
                                    else:
                                        self.s.send('PRIVMSG ' + priv_chan + ' :Not enough parameter: ' + cmd_prefix + msg_enable + ' <#channel>\n')
            
                            if data[3] == (":" + cmd_prefix + msg_disable):
                                channel = data[2]
                                if channel == priv_chan:
                                    if len(data) == 5:
                                        if "#" in data[4]:
                                            self.cursor.execute("UPDATE 1_peng_bots SET ablemsg='off' WHERE channel='" + data[4] + "'")
                                            self.s.send('PRIVMSG ' + priv_chan + ' :#DISABLED#\n')
                                        else:
                                            self.s.send('PRIVMSG ' + priv_chan + ' :Channel missing: ' + cmd_prefix + msg_enable + ' <#channel>\n')
                                    else:
                                        self.s.send('PRIVMSG ' + priv_chan + ' :Not enough parameter: ' + cmd_prefix + msg_enable + ' <#channel>\n')
            
                            if data[3] == (":" + cmd_prefix + gtv_enable):
                                channel = data[2]
                                if channel == priv_chan:
                                    if len(data) == 5:
                                        if "#" in data[4]:
                                            self.cursor.execute("UPDATE 1_peng_bots SET ablegtv='on' WHERE channel='" + data[4] + "'")
                                            self.s.send('PRIVMSG ' + priv_chan + ' :#ENABLED#\n')
                                        else:
                                            self.s.send('PRIVMSG ' + priv_chan + ' :Channel missing: ' + cmd_prefix + gtv_enable + ' <#channel>\n')
                                    else:
                                        self.s.send('PRIVMSG ' + priv_chan + ' :Not enough parameter: ' + cmd_prefix + gtv_enable + ' <#channel>\n')
            
                            if data[3] == (":" + cmd_prefix + gtv_disable):
                                channel = data[2]
                                if channel == priv_chan:
                                    if len(data) == 5:
                                        if "#" in data[4]:
                                            self.cursor.execute("UPDATE 1_peng_bots SET ablegtv='off' WHERE channel='" + data[4] + "'")
                                            self.s.send('PRIVMSG ' + priv_chan + ' :#DISABLED#\n')
                                        else:
                                            self.s.send('PRIVMSG ' + priv_chan + ' :Channel missing: ' + cmd_prefix + gtv_enable + ' <#channel>\n')
                                    else:
                                        self.s.send('PRIVMSG ' + priv_chan + ' :Not enough parameter: ' + cmd_prefix + gtv_enable + ' <#channel>\n')
                                        
                            if data[3] == (":" + cmd_prefix + "amsg"):
                                channel = data[2]
                                if channel == priv_chan:
                                    if len(data) >= 5:
                                        stop = 0
                                        num = 4
                                        what = ""
                                        lenge = len(data)
                                        while(stop < 1):
                                            what = what  + " " + data[int(num)]
                                            num = int(num) + 1
                                            if int(num) == int(lenge):
                                                stop = 1
                                            if "\'" in what:
                                                what = what.replace("\'", "`")
                                        self.cursor.execute("INSERT INTO `1_peng_messages` (`type`, `channel`, `nick`, `auth`, `number`, `message`, `active`, `date`, `time`, `month`) VALUES ('amsg', '" + pub_chan + "', '" + str(nick) +"', '', '', '" + str(what) + "', 'yes', '" + str(getdate) + "', '" + str(gettime) + "', '" + str(getmonth) + "')")
                                        self.cursor.execute("SELECT id FROM 1_peng_messages WHERE type='amsg' ORDER BY id DESC")
                                        mid = self.cursor.fetchone()
                                        mid = mid[0]
                                        self.s.send('PRIVMSG #peng.ubber.priv :' + sup_spam + ' amsg ' + str(mid) + '\n')
                                    else:
                                        self.s.send('PRIVMSG ' + channel + ' :' + cmd_prefix + 'amsg <text>\n')
                except:
                    text = text.replace("'", "`")
                    self.s.close()
                    print "DIE"
                    traceback.print_exc(file=sys.stdout)
                    sys.exit()                
                else:
                    sleep(3)
                         
##[END - PengMaster Class]##

##[BEGIN - PengBot Class]##
class botPeng(Thread):
    def __init__(self, botID, useprint):
        Thread.__init__(self)
        self.botID = botID
        self.useprint = useprint

        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host
        self.port = random.choice([6665,6666,6668,6669])
        self.nick = "pengbot" + botID
        self.realname = "pengbot " + version
        self.identt = "peng" + botID
        self.readbuffer = ""
        
        self.gettime = ""
        self.getdate = ""
        self.getall = ""
        self.getmonth = ""
        self.getyear = ""

        self.stop = False
        
        self.mysql = MySQLdb.connect (host = db_host,
                                 user = db_user,
                                 passwd = db_passwd,
                                 db = db_db)
        self.cursor = self.mysql.cursor()

        #self.s_mysql = MySQLdb.connect (host = db1_host,
        #                         user = db1_user,
        #                         passwd = db1_passwd,
        #                         db = db1_db)
        #self.statistic = self.s_mysql.cursor()
    def normalize_day(self, day):
        if len(day) == 1:
            return "0" + day
        else:
            return day
    
    def check_auth(self, nick):
        self.cursor.execute("SELECT * FROM 1_peng_auth WHERE Nick='" + nick + "'")
        getauth = self.cursor.fetchone()
        if getauth != None:
            return True
        else:
            self.s.send('WHOIS ' + nick + '\n')
            return False
    
    def check_ban(self, nick):
        self.cursor.execute("SELECT AuthNick FROM 1_peng_auth WHERE Nick='" + nick + "'")
        auth = self.cursor.fetchone()
        auth = auth[0]
        self.cursor.execute("SELECT * FROM 1_peng_ban WHERE Auth='" + str(auth) + "'")
        getban = self.cursor.fetchone()
        if getban != None:
            return True
        else:
            return False
    
    def flood_prot(self, channel, nick, kind):
        self.cursor.execute("SELECT AuthNick FROM 1_peng_auth WHERE Nick='" + nick + "'")
        auth = self.cursor.fetchone()
        auth = auth[0]
        self.cursor.execute("SELECT * FROM 1_peng_messages WHERE active='yes'")
        access = self.cursor.fetchall()
        sstop = 0
        num = 0
        result = 0
        if not len(access) == 0:
            while(sstop < 1):
                if num < len(access):
                    iaccess = access[num]
                    if auth in iaccess[4] or channel in iaccess[2]:
                        pengtime = iaccess[9].split(":")
                        pengmin = int(pengtime[1]) * 60
                        penghour = int(pengtime[0]) * 3600
                        pengtime = int(penghour) + int(pengmin) + int(pengtime[2])
                        newtime = self.gettime.split(":")
                        newmin = int(newtime[1]) * 60
                        newhour = int(newtime[0]) * 3600
                        newtime = int(newhour) + int(newmin) + int(newtime[2])
                        if (newtime - pengtime) < 600:
                            timeleft = 600 - (newtime - pengtime)
                            self.s.send('PRIVMSG ' + channel + ' :['+ kind +'] You can\'t spam so fast. Next spam in ' + str(timeleft) + ' seconds\n')
                            result = 1
                            sstop = 1
                    num = num + 1
                else:
                    sstop = 1
                    
        if result == 0:
            return True
        else:
            return False
    
    def text_addinfo(self, data,start):
        stop = 0
        num = start
        what = ""
        lenge = len(data)
        while(stop < 1):
            if num == start:
                what = data[int(num)]
            else:
                what = what  + " " + data[int(num)]
            num = int(num) + 1
            if int(num) == int(lenge):
                stop = 1
        if "\'" in what:
            what = what.replace("\'", "`")
        return what
    
    def submit_match(self, nick,data,channel,kind):
        small_let = kind.lower()
        self.cursor.execute("SELECT AuthNick FROM 1_peng_auth WHERE Nick='" + nick + "'")
        auth = self.cursor.fetchone()
        auth = auth[0]
        self.getyear=self.getdate.split(".")
        self.getyear=self.getyear[2]
        if kind != "MSG" and kind != "GTV":
            if len(data) == 5:
                if data[4].isdigit() and len(data[4]) == 1:
                    self.cursor.execute("INSERT INTO `1_peng_messages` (`type`, `channel`, `nick`, `auth`, `number`, `message`, `active`, `date`, `time`, `month`) VALUES ('" + small_let + "', '" + str(channel) +"', '" + str(nick) +"', '" + str(auth) +"', '" + str(data[4]) + "', '', 'yes', '" + str(self.getdate) + "', '" + str(self.gettime) + "', '" + str(self.getyear) + str(self.getmonth) + "')")
                    self.s.send('PRIVMSG ' + channel + ' :[' + kind + '] Successfully spammed!\n')
                    #msg an super peng
                    self.cursor.execute("SELECT id FROM 1_peng_messages WHERE type='" + small_let + "' AND Date='" + str(self.getdate) + "' AND Time='" + str(self.gettime) + "' AND Nick='" + str(nick) + "' AND Channel='" + str(channel) +"' ORDER BY id DESC")
                    mid = self.cursor.fetchone()
                    mid = mid[0]
                    self.s.send('PRIVMSG ' + priv_chan + ' :' + bot_new + ' ' + kind + ' ' + str(mid) + '\n')
                else:
                    self.s.send('PRIVMSG ' + channel + ' :' + cmd_prefix + small_let + ' <number> </info/>\n')
            elif len(data) >= 6:
                if data[4].isdigit() and len(data[4]) == 1:
                    what = self.text_addinfo(data, 5) #Function
                    info = "%s" %(str(what))
                    self.cursor.execute("INSERT INTO `1_peng_messages` (`type`, `channel`, `nick`, `auth`, `number`, `message`, `active`, `date`, `time`, `month`) VALUES ('" + small_let + "', '" + str(channel) +"', '" + str(nick) +"', '" + str(auth) + "', '" + str(data[4]) + "', '" + str(info) + "', 'yes', '" + str(self.getdate) + "', '" + str(self.gettime) + "', '" + str(self.getyear) + str(self.getmonth) + "')")
                    self.s.send('PRIVMSG ' + channel + ' :[' + kind + '] Successfully spammed!\n')
                    #msg an super peng
                    self.cursor.execute("SELECT id FROM 1_peng_messages WHERE type='" + small_let + "' AND Date='" + str(self.getdate) + "' AND Time='" + str(self.gettime) + "' AND Nick='" + str(nick) + "' AND Channel='" + str(channel) +"' ORDER BY id DESC")
                    mid = self.cursor.fetchone()
                    mid = mid[0]
                    self.s.send('PRIVMSG ' + priv_chan + ' :' + bot_new + ' ' + kind + ' ' + str(mid) + '\n')
                else:
                    self.s.send('PRIVMSG ' + channel + ' :' + cmd_prefix + small_let + ' <1-9> </info/>\n')
            else:
                self.s.send('PRIVMSG ' + channel + ' :' + cmd_prefix + small_let + ' <number> </info/>\n')
                
        else:
            if len(data) >= 5:
                what = self.text_addinfo(data,4) #Function
                info = "%s" %(str(what))
                self.cursor.execute("INSERT INTO `1_peng_messages` (`type`, `channel`, `nick`, `auth`, `number`, `message`, `active`, `date`, `time`, `month`) VALUES ('" + small_let + "', '" + str(channel) + "', '" + str(nick) +"', '" + str(auth) +"', '', '" + str(info) + "', 'yes', '" + str(self.getdate) + "', '" + str(self.gettime) + "', '" + str(self.getyear) + str(self.getmonth) + "')")
                self.s.send('PRIVMSG ' + channel + ' :[' + kind + '] Successfully spammed!\n')
                #msg an super peng
                self.cursor.execute("SELECT id FROM 1_peng_messages WHERE type='" + small_let + "' ORDER BY id DESC")
                mid = self.cursor.fetchone()
                mid = mid[0]
                self.s.send('PRIVMSG ' + priv_chan + ' :' + bot_new + ' ' + kind + ' ' + str(mid) + '\n')
            else:
                self.s.send('PRIVMSG ' + channel + ' :' + cmd_prefix + small_let + ' <text>\n')
    
    def spam_match(self, data,channel,kind):
        if kind == "pcw":
            msg = spam_pcw
        elif kind == "cw":
            msg = spam_cw
        elif kind == "ringer":
            msg = spam_ringer
        elif kind == "recruit":
            msg = spam_recruit
        elif kind == "msg":
            msg = spam_msg
        elif kind == "gtv":
            msg = spam_gtv
        elif kind == "amsg":
            msg = spam_amsg
        self.cursor.execute("SELECT channel FROM 1_peng_bots WHERE " + kind + "='on' AND id='" + self.botID + "'")
        chan = self.cursor.fetchall()
        lenge = len(chan) - 1
        self.cursor.execute("SELECT * FROM 1_peng_messages WHERE id='" + data[5] + "'")
        peng = self.cursor.fetchone()
        if peng[6] == "":
            msg = msg.split(".start.")
            msg = msg[0]
        else:
            msg = msg.replace(".start.", "")
        msg = msg.replace(".channel.", peng[2])
        msg = msg.replace(".nick.", peng[3])
        msg = msg.replace(".number.", peng[5])
        msg = msg.replace(".info.", peng[6])
        if lenge >= 0:
            stop = 0
            number = 0
            while(stop < 1):
                if lenge >= 0:
                    if not peng[2] == chan[lenge][0]:
                        self.s.send('PRIVMSG ' + chan[lenge][0] + ' :' + msg + '\n')
                        sleep(2.5)
                else:
                    stop = 1
                lenge = lenge - 1
    
    def set_display(self, data,channel,kind):
        if kind == "pcw":
            big_let = "DISPLAYPCW"
            show_kind = show_pcw
        elif kind == "cw":
            big_let = "DISPLAYCW"
            show_kind = show_cw
        elif kind == "ringer":
            big_let = "DISPLAYRINGER"
            show_kind = show_ringer
        elif kind == "recruit":
            big_let = "DISPLAYRECRUIT"
            show_kind = show_recruit
        elif kind == "msg":
            big_let = "DISPLAYMSG"
            show_kind = show_msg
        elif kind == "gtv":
            big_let = "DISPLAYGTV"
            show_kind = show_gtv
        elif kind == "pickup":
            big_let = "PICKUP"
            show_kind = enable_pickup
        if len(data) == 5:
            if data[4] == "on":
                self.cursor.execute("SELECT " + kind + " FROM 1_peng_bots WHERE id='" + self.botID + "' AND channel='" + channel + "'")
                peng = self.cursor.fetchone()
                peng_pcw = peng[0]
                if peng_pcw == "on":
                    self.s.send('PRIVMSG ' + channel + ' :[' + big_let + '] Already on\n')
                else:
                    self.s.send('PRIVMSG ' + channel + ' :[' + big_let + '] Turned on\n')
                    self.cursor.execute("UPDATE 1_peng_bots SET " + kind + "='on' WHERE id='" + self.botID + "' AND channel='" + str(channel) + "'")
            elif data[4] == "off":
                self.cursor.execute("SELECT " + kind + " FROM 1_peng_bots WHERE id='" + self.botID + "' AND channel='" + channel + "'")
                peng = self.cursor.fetchone()
                peng_pcw = peng[0]
                if peng_pcw == "off":
                    self.s.send('PRIVMSG ' + channel + ' :[' + big_let + '] Already off\n')
                else:
                    self.s.send('PRIVMSG ' + channel + ' :[' + big_let + '] Turned off\n')
                    self.cursor.execute("UPDATE 1_peng_bots SET " + kind + "='off' WHERE id='" + self.botID + "' AND channel='" + str(channel) + "'")
            else:
                self.s.send('PRIVMSG ' + channel + ' :' + cmd_prefix + show_kind + ' <on/off>\n')
    
    def show_list(self, channel,gettime,kind):
        if kind == "pcw":
            msg = display_pcw
            big_let = "PCW"
        elif kind == "cw":
            msg = display_cw
            big_let = "CW"
        elif kind == "ringer":
            msg = display_ringer
            big_let = "RINGER"
        elif kind == "recruit":
            msg = display_recruit
            big_let = "RECRUIT"
        elif kind == "msg":
            msg = display_msg
            big_let = "MSG"
        elif kind == "gtv":
            msg = display_gtv
            big_let = "GTV"
        self.cursor.execute("SELECT * FROM 1_peng_messages WHERE type='" + kind + "' AND (active='yes' OR active='free') ORDER BY id DESC limit 15")
        peng = self.cursor.fetchall()
        stop = 0
        result = 0
        num = 0
        while(stop < 1):
            if num < len(peng):
                peng1 = peng[num]
                if peng1[6] == "":
                    if ".end." in msg:
                        msg1 = msg.split(".end.")
                        msg1 = msg1[1]
                    s_msg = msg.split(".start.")
                    s_msg = s_msg[0]
                    s_msg = s_msg + msg1
                else:
                    s_msg = msg.replace(".start.","")
                    s_msg = s_msg.replace(".end.","")
                s_msg = s_msg.replace(".channel.", peng1[2])
                s_msg = s_msg.replace(".nick.", peng1[3])
                s_msg = s_msg.replace(".number.", peng1[5])
                s_msg = s_msg.replace(".info.", peng1[6])
                pengtime = peng1[9]
                pengtime = pengtime.split(":")
                pengtime[0] = int(pengtime[0]) * 60
                pengtime = pengtime[0] + int(pengtime[1])
                newtime = gettime.split(":")
                newtime[0] = int(newtime[0]) * 60
                newtime = newtime[0] + int(newtime[1])
                minutes = int(newtime) - int(pengtime)
                s_msg = s_msg.replace(".time.", str(minutes))
                self.s.send('PRIVMSG ' + channel + ' :' + s_msg + '\n')
                result = 1
                sleep(2)
            else:
                if result == 0:
                    self.s.send('PRIVMSG ' + channel + ' :[' + big_let + 'LIST] No ' + kind + 's in the last 30 minutes\n')
                stop = 1
            num = num + 1
    
    def botauth(self):
        self.cursor.execute("SELECT authnick,authpass FROM 1_peng_botauth WHERE botid='" + self.botID + "'")
        authing_all = self.cursor.fetchone()
        authing_name = authing_all[0]
        authing_pass = authing_all[1]
        return authing_name + " " + authing_pass
    
    def peng_enable(self, chan):
        self.cursor.execute("SELECT * FROM 1_peng_bots WHERE channel='" + chan + "' AND pickup='on'")
        is_enabled = self.cursor.fetchone()
        if is_enabled != None:
            return True
        else:
            return False
    
    def peng_lock(self):
        self.cursor.execute("SELECT * FROM 1_peng_status WHERE name='lock' AND status='1'")
        is_locked = self.cursor.fetchone()
        if is_locked != None:
            return True
        else:
            return False
        
    def peng_gamestarted(self):
        self.cursor.execute("SELECT * FROM 1_peng_status WHERE name='game' AND status='1'")
        game_started = self.cursor.fetchone()
        if game_started != None:
            return True
        else:
            return False
        
    def peng_add(self, channel,nick):
        self.cursor.execute("SELECT id,name FROM 1_peng_player ORDER BY id")
        players = self.cursor.fetchall()
        num = 0
        self.cursor.execute("SELECT AuthNick FROM 1_peng_auth WHERE Nick='" + nick + "'")
        auth = self.cursor.fetchone()
        auth = auth[0]
        self.cursor.execute("SELECT * FROM 1_peng_player WHERE name='" + nick + "'")
        is_playing = self.cursor.fetchone()
        if is_playing == None:
            self.cursor.execute("SELECT status FROM 1_peng_status WHERE name='players'")
            playernum = self.cursor.fetchone()
            playernum = int(playernum[0])
            playernum = playernum + 1
            self.cursor.execute("UPDATE 1_peng_status SET status='" + str(playernum) + "' WHERE name='players'")
            while(num < len(players)):
                if players[num][1] == "":
                    self.cursor.execute("UPDATE 1_peng_player SET name='" + str(nick) + "' WHERE id='" + players[num][0] + "'")
                    self.cursor.execute("UPDATE 1_peng_player SET qauth='" + str(auth) + "' WHERE id='" + players[num][0] + "'")
                    self.cursor.execute("UPDATE 1_peng_player SET botid='" + str(self.botID) + "' WHERE id='" + players[num][0] + "'")
                    self.cursor.execute("UPDATE 1_peng_player SET captain='0' WHERE id='" + players[num][0] + "'")
                    self.cursor.execute("UPDATE 1_peng_player SET mode='0' WHERE id='" + players[num][0] + "'")
                    self.cursor.execute("UPDATE 1_peng_player SET map='0' WHERE id='" + players[num][0] + "'")
                    num = len(players)
                num = num + 1
            self.peng_status(channel)
        else:
            self.s.send('NOTICE ' + nick + ' :' + already_added + '\n')
        self.s.send('PRIVMSG ' + priv_chan + ' :' + info_update + '\n')
    
    def peng_remove(self, channel,nick):
        self.cursor.execute("SELECT id,name FROM 1_peng_player ORDER BY id")
        players = self.cursor.fetchall()
        num = 0
        self.cursor.execute("SELECT map,mode FROM 1_peng_player WHERE name='" + nick + "'")
        is_playing = self.cursor.fetchone()
        if is_playing != None:
            self.cursor.execute("SELECT status FROM 1_peng_status WHERE name='players'")
            playernum = self.cursor.fetchone()
            playernum = int(playernum[0])
            playernum = playernum - 1
            self.cursor.execute("UPDATE 1_peng_status SET status='" + str(playernum) + "' WHERE name='players'")
            while(num < len(players)):
                if players[num][1] == nick:
                    self.cursor.execute("UPDATE 1_peng_player SET name='' WHERE id='" + players[num][0] + "'")
                    self.cursor.execute("UPDATE 1_peng_player SET botid='' WHERE id='" + players[num][0] + "'")
                    self.cursor.execute("UPDATE 1_peng_player SET captain='0' WHERE id='" + players[num][0] + "'")
                    if str(is_playing[0]) != '0':
                        self.cursor.execute("SELECT id,vote FROM 1_peng_map WHERE id='" + is_playing[0] + "'")
                        maps = self.cursor.fetchone()
                        self.cursor.execute("UPDATE 1_peng_map SET vote='" + str(int(maps[1]) - 1) + "' WHERE id='" + str(maps[0]) + "'")
                        self.cursor.execute("UPDATE 1_peng_player SET map='0' WHERE id='" + players[num][0] + "'")
                    if str(is_playing[1]) != '0':
                        self.cursor.execute("SELECT id,vote FROM 1_peng_mode WHERE id='" + is_playing[1] + "'")
                        modes = self.cursor.fetchone()
                        self.cursor.execute("UPDATE 1_peng_mode SET vote='" + str(int(modes[1]) - 1) + "' WHERE id='" + str(modes[0]) + "'")
                        self.cursor.execute("UPDATE 1_peng_player SET mode='0' WHERE id='" + players[num][0] + "'")
                    num = len(players)
                num = num + 1
            self.s.send('PRIVMSG ' + priv_chan + ' :' + info_update + '\n')
            self.peng_status(channel)
        else:
            self.s.send('NOTICE ' + nick + ' :' + not_added + '\n')
    
    def peng_quit(self, nick):
        self.cursor.execute("SELECT id,name FROM 1_peng_player ORDER BY id")
        players = self.cursor.fetchall()
        num = 0
        self.cursor.execute("SELECT map,mode FROM 1_peng_player WHERE name='" + nick + "'")
        is_playing = self.cursor.fetchone()
        if is_playing != None:
            self.cursor.execute("SELECT status FROM 1_peng_status WHERE name='players'")
            playernum = self.cursor.fetchone()
            playernum = int(playernum[0])
            playernum = playernum - 1
            self.cursor.execute("UPDATE 1_peng_status SET status='" + str(playernum) + "' WHERE name='players'")
            while(num < len(players)):
                if players[num][1] == nick:
                    self.cursor.execute("UPDATE 1_peng_player SET name='' WHERE id='" + players[num][0] + "'")
                    self.cursor.execute("UPDATE 1_peng_player SET qauth='' WHERE id='" + players[num][0] + "'")
                    self.cursor.execute("UPDATE 1_peng_player SET botid='' WHERE id='" + players[num][0] + "'")
                    self.cursor.execute("UPDATE 1_peng_player SET captain='0' WHERE id='" + players[num][0] + "'")
                    if is_playing[0] != '0':
                        self.cursor.execute("SELECT id,vote FROM 1_peng_map WHERE id=" + int(is_playing[0]))
                        maps = self.cursor.fetchone()
                        self.cursor.execute("UPDATE 1_peng_map SET vote='" + str(int(maps[1]) - 1) + "' WHERE id='" + str(maps[0]) + "'")
                        self.cursor.execute("UPDATE 1_peng_player SET map='0' WHERE id='" + players[num][0] + "'")
                    if is_playing[1] != '0':
                        self.cursor.execute("SELECT id,vote FROM 1_peng_mode WHERE id=" + int(is_playing[1]))
                        modes = self.cursor.fetchone()
                        self.cursor.execute("UPDATE 1_peng_mode SET vote='" + str(int(modes[1]) - 1) + "' WHERE id='" + str(modes[0]) + "'")
                        self.cursor.execute("UPDATE 1_peng_player SET mode='0' WHERE id='" + players[num][0] + "'")
                    num = len(players)
                num = num + 1
            self.s.send('PRIVMSG ' + priv_chan + ' :' + info_update + '\n')
            
    def peng_maps(self, channel):
        self.cursor.execute("SELECT map,vote FROM 1_peng_map ORDER BY id")
        maps = self.cursor.fetchall()
        maplist = ''
        map_check = str(maps)
        if map_check != '()':
            num = 0
            while(num < len(maps)):
                if maplist == '':
                    maplist = maps[num][0] + ": " + maps[num][1]
                else:
                    maplist = maplist + " | " + maps[num][0] + ": " + maps[num][1]
                num = num + 1
            self.s.send('PRIVMSG ' + channel + ' :' + maplist + '\n')
        else:
            self.s.send('PRIVMSG ' + channel + ' :' + self.no_map_added + '\n')
    
    def peng_modes(self, channel):
        self.cursor.execute("SELECT mode,vote FROM 1_peng_mode ORDER BY id")
        modes = self.cursor.fetchall()
        modelist = ''
        mode_check = str(modes)
        if mode_check != '()':
            num = 0
            while(num < len(modes)):
                if modelist == '':
                    modelist = modes[num][0] + ": " + modes[num][1]
                else:
                    modelist = modelist + " | " + modes[num][0] + ": " + modes[num][1]
                num = num + 1
            self.s.send('PRIVMSG ' + channel + ' :' + modelist + '\n')
        else:
            self.s.send('PRIVMSG ' + channel + ' :' + self.no_mode_added + '\n')
    
    def peng_vote(self, channel,nick,data,text):
        self.cursor.execute("SELECT map,mode FROM 1_peng_player WHERE name='" + nick + "'")
        votelist = self.cursor.fetchone()
        if votelist != None:
            msg = ''
            replacer = data[0] + " " + data[1] + " " + data[2] + " " + data[3] + " " + data[4]
            text = text.replace(replacer, '')
            if votelist[0] == "0":
                self.cursor.execute("SELECT map,vote,id FROM 1_peng_map ORDER BY id")
                maps = self.cursor.fetchall()
                map_check = str(maps)
                if map_check != '()':
                    num = 0
                    while(num < len(maps)):
                        without_ut4 = maps[num][0].replace('ut4_', '')
                        if without_ut4 in text:
                            self.cursor.execute("UPDATE 1_peng_map SET vote='" + str(int(maps[num][1]) + 1) + "' WHERE id=" + str(maps[num][2]))
                            self.cursor.execute("UPDATE 1_peng_player SET map='" + str(maps[num][2]) + "' WHERE name='" + str(nick) + "'")
                            if msg == '':
                                msg = '[PICKUP] ' + pkup_map
                            else:
                                msg = msg + " " + pkup_map
                            num = len(maps)
                        num = num + 1
                else:
                    self.s.send('PRIVMSG ' + channel + ' :' + self.no_map_added + '\n')
                    
            if votelist[1] == "0":
                self.cursor.execute("SELECT mode,vote,id FROM 1_peng_mode ORDER BY id")
                modes = self.cursor.fetchall()
                mode_check = str(modes)
                if mode_check != '()':
                    num = 0
                    while(num < len(modes)):
                        if modes[num][0] in text:
                            self.cursor.execute("UPDATE 1_peng_mode SET vote='" + str(int(modes[num][1]) + 1) + "' WHERE id=" + str(modes[num][2]))
                            self.cursor.execute("UPDATE 1_peng_player SET mode='" + str(modes[num][2]) + "' WHERE name='" + str(nick) + "'")
                            if msg == '':
                                msg = '[PICKUP] ' + pkup_mode
                            else:
                                msg = msg + " " + pkup_mode
                            num = len(modes)
                        num = num + 1
                else:
                    self.s.send('PRIVMSG ' + channel + ' :' + self.no_mode_added + '\n')
                    
            if msg != '':
                self.s.send('NOTICE ' + nick + ' :' + msg + '\n')
            else:
                self.s.send('NOTICE ' + nick + ' :' + pkup_mm + '\n')
            
        else:
            self.s.send('NOTICE ' + nick + ' :' + not_added + '\n')
        
    def peng_pw(self, nick, channel):
        self.cursor.execute("SELECT * FROM 1_peng_player WHERE name='" + nick + "'")
        is_player = self.cursor.fetchone()
        if is_player != None:
            self.cursor.execute("SELECT status FROM 1_peng_status WHERE name='server'")
            server = self.cursor.fetchone()
            server = server[0]
            self.cursor.execute("SELECT status FROM 1_peng_status WHERE name='password'")
            password = self.cursor.fetchone()
            password = password[0]
            msg = pkup_pw.replace(".server.", server)
            msg = msg.replace(".password.", password)
            self.s.send('PRIVMSG ' + nick + ' :' + msg + '\n')
        else:
            self.s.send('PRIVMSG ' + channel + ' :' + not_added + '\n')
            
    def peng_status(self, channel):
        self.cursor.execute("SELECT status FROM 1_peng_status WHERE name='players'")
        playernum = self.cursor.fetchone()
        playernum = int(playernum[0])
        if playernum > 0:
            msg = pkup_status1.replace(".playernumber.", str(playernum))
        else:
            msg = pkup_status2
        self.s.send('PRIVMSG ' + priv_chan + ' :' + info_update + '\n')
        self.s.send('PRIVMSG ' + channel + ' :' + msg + '\n')
         
    def peng_players(self, channel, nick): 
        self.cursor.execute("SELECT status FROM 1_peng_status WHERE name='players'")
        playernum = self.cursor.fetchone()
        playernum = int(playernum[0])
        if playernum > 0:
            playerlist = ''
            self.cursor.execute("SELECT name FROM 1_peng_player WHERE NOT name=''")
            get_playerlist = self.cursor.fetchall()
            num = 0
            while(num < len(get_playerlist)):
                if playerlist == '':
                    playerlist = get_playerlist[num][0]
                else:
                    playerlist = playerlist + " " + get_playerlist[num][0]
                num = num + 1
            msg = pkup_players.replace('.playernumber.', str(playernum))
            msg = msg.replace('.playerlist.', str(playerlist))
            self.s.send('NOTICE ' + nick + ' :' + msg + '\n')
        else:
            msg = pkup_status2
            self.s.send('PRIVMSG ' + channel + ' :' + msg + '\n')
        
    def peng_gameover(self, channel,nick):
        self.cursor.execute("SELECT gameover FROM 1_peng_player WHERE name='" + nick + "'")
        is_player = self.cursor.fetchone()
        if is_player != None:
            if is_player[0] == "":
                self.cursor.execute("SELECT status FROM 1_peng_status WHERE name='gameover'")
                gameover = self.cursor.fetchone()
                gameover = gameover[0]
                gameover = int(gameover) - 1
                self.cursor.execute("UPDATE 1_peng_status SET status='" + str(gameover) + "' WHERE name='gameover'")
                self.cursor.execute("UPDATE 1_peng_player SET gameover='1' WHERE name='" + nick + "'")
                if gameover != "0":
                    self.s.send('PRIVMSG ' + priv_chan + ' :' + info_gameover + ' ' + nick + '\n')
                    msg = pkup_gameover_a.replace(".nick.", nick)
                    msg = msg.replace(".gameoverleft.", str(gameover))
                    self.s.send('PRIVMSG ' + channel + ' :' + msg + '\n')
                    self.peng_spam(nick,'gameover',channel)
                else:
                    self.s.send('PRIVMSG ' + priv_chan + ' :' + info_update + '\n')
            else:
                self.s.send('PRIVMSG ' + channel + ' :' + already_gameover + '\n')
        else:
            self.s.send('PRIVMSG ' + channel + ' :' + not_added + '\n')
            
    def peng_help(self, channel, nick):
        if "peng" in channel:
            if self.botID == "001":
                self.s.send('NOTICE ' + nick + ' :This command is disabled in this channel! \n')
        else:
            self.s.send('PRIVMSG ' + channel + ' :' + url_help + '\n')
    
    def peng_spam(self, nick,kind,channel):
        if kind == "gameover":
            self.cursor.execute("SELECT status FROM 1_peng_status WHERE name='gameover'")
            gameover = self.cursor.fetchone()
            gameover = gameover[0]
            msg = pkup_gameover_b
            msg = msg.replace(".nick.", nick)
            msg = msg.replace(".gameoverleft.", str(gameover))
        elif kind == "signup":
            msg = pkup_signup
        elif kind == "datasent":
            msg = pkup_go_sent
        self.cursor.execute("SELECT channel FROM 1_peng_bots WHERE id='" + self.botID + "' AND pickup='on'")
        spam_chans = self.cursor.fetchall()
        num = 0
        while(num < len(spam_chans)):
            if spam_chans[num][0] != channel:
                self.s.send('PRIVMSG ' + spam_chans[num][0] + ' :' + msg + '\n')
            num = num + 1
    
    def peng_pm(self):
        self.cursor.execute("SELECT name,captain FROM 1_peng_player WHERE botid='" + self.botID  + "' AND NOT captain='1' ORDER BY captain DESC")
        players = self.cursor.fetchall()
        self.cursor.execute("SELECT map FROM 1_peng_map ORDER BY vote DESC")
        votes = self.cursor.fetchone()
        smap = str(votes[0])
        self.cursor.execute("SELECT mode FROM 1_peng_mode ORDER BY vote DESC")
        votes = self.cursor.fetchone()
        stype = str(votes[0])
        self.cursor.execute("SELECT status FROM 1_peng_status WHERE name='server'")
        server = self.cursor.fetchone()
        server = str(server[0])
        self.cursor.execute("SELECT status FROM 1_peng_status WHERE name='password'")
        password = self.cursor.fetchone()
        password = str(password[0])
        msgcap = self.pkup_go_cap.replace(".type.", stype)
        msgcap = msgcap.replace(".map.", smap)
        msgcap = msgcap.replace(".server.", server)
        msgcap = msgcap.replace(".password.", password)
        msgply = pkup_go_player.replace(".type.", stype)
        msgply = msgply.replace(".map.", smap)
        msgply = msgply.replace(".server.", server)
        msgply = msgply.replace(".password.", password)
        num = 0
        count = 0
        self.cursor.execute("SELECT name,captain FROM 1_peng_player WHERE captain='1' ORDER BY captain DESC")
        playercap = self.cursor.fetchall()
        captain1=playercap[0][0]
        captain2=playercap[1][0]
        while(num < len(players)):
            if players[num][0] == captain1:
                msgcap = msgcap.replace(".captain.", captain2)
                self.s.send('PRIVMSG ' + players[num][0] + ' :' + msgcap + '\n')
            elif players[num][0] == captain2:
                msgcap = msgcap.replace(".captain.", captain1)
                self.s.send('PRIVMSG ' + players[num][0] + ' :' + msgcap + '\n')
            else:
                self.s.send('PRIVMSG ' + players[num][0] + ' :' + msgply + '\n')
            sleep(2)
            count = count + 1
            num = num + 1
        if count != 0:
            self.s.send('PRIVMSG ' + priv_chan + ' :' + self.info_sentto + ' ' + str(count) + '\n')
    
    def small(self, text):
        return text.lower()
    
    def farbreplace(self, text):
        num = 0
        name = ""
        while(num < len(text)):
            if text[num] == "^":
                num = num + 1
            else:
                name = name + text[num]
            num = num +1
        return name
    
    def gametype(self, gtype):
        if gtype == "0":
            gtype = "FFA"
        elif gtype == "3":
            gtype = "TDM"
        elif gtype == "4":
            gtype = "TS"
        elif gtype == "5":
            gtype = "FTL"
        elif gtype == "6":
            gtype = "C&H"
        elif gtype == "7":
            gtype = "CTF"
        elif gtype == "8":
            gtype = "BOMB"
        else:
            gtype = "???"
        return gtype
    
    def find_player(self, channel,player):
        f_player = self.small(player)#Function
        self.s.send('PRIVMSG ' + channel + ' :Query database [...]\n')
        self.statistic.execute("SELECT player_name,player_serverid FROM players_list")
        players = self.statistic.fetchall()
        num = 0
        results = 0
        while (num < len(players)):
            fname = players[num][0]
            fname = self.small(fname)
            fname = self.farbreplace(fname)
            if f_player in fname:
                self.statistic.execute("SELECT query_name,query_map FROM querys_list WHERE query_serverid='" + str(players[num][1]) + "'")
                server_info = self.statistic.fetchone()
                sname = self.farbreplace(server_info[0])
                smap = server_info[1]
                self.statistic.execute("SELECT server_ip FROM servers_list WHERE server_id='" + str(players[num][1]) + "'")
                server_ip = self.statistic.fetchone()
                sip = server_ip[0]
                self.s.send('PRIVMSG ' + channel + ' :' + fname + " | " + sname + " - " + sip + " - " + smap + '\n')
                results = results + 1
                sleep(2)
                if int(results) == 5:
                    self.s.send('PRIVMSG ' + channel + ' :At least 5 players [...]\n')
                    break
            num = num + 1
        if (0 < results < 5):
            self.s.send('PRIVMSG ' + channel + ' :End of list [...]\n')
        if results == 0:
            self.s.send('PRIVMSG ' + channel + ' :No players currently playing\n')
    
    def find_name(self, channel,name):
        f_name = self.small(name)#Function
        self.s.send('PRIVMSG ' + channel + ' :Query database [...]\n')
        self.statistic.execute("SELECT query_serverid,query_name,query_map,query_gametype,query_players,query_publicslots FROM querys_list")
        servers = self.statistic.fetchall()
        num = 0
        results = 0
        while (num < len(servers)):
            fname = servers[num][1]
            fname = self.small(fname)
            fname = self.farbreplace(fname)
            if f_name in fname:
                self.statistic.execute("SELECT server_ip FROM servers_list WHERE server_id='" + str(servers[num][0]) + "'")
                server_ip = self.statistic.fetchone()
                sip = str(server_ip[0])
                sname = str(servers[num][1])
                sname = self.farbreplace(sname)
                smap = str(servers[num][2])
                gtype = str(servers[num][3])
                gtype = str(self.gametype(gtype))
                sslots = str(servers[num][4])
                smaxplayer = str(servers[num][5])
                self.s.send('PRIVMSG ' + channel + ' :' + sip + " - " + sname + " - " + smap + " - " + gtype + " | " + sslots + '/' + smaxplayer + '\n')
                results = results + 1
                sleep(2)
                if int(results) == 5:
                    self.s.send('PRIVMSG ' + channel + ' :At least 5 servers [...]\n')
                    break
            num = num + 1
        if (0 < results < 5):
            self.s.send('PRIVMSG ' + channel + ' :End of list [...]\n')
        if results == 0:
            self.s.send('PRIVMSG ' + channel + ' :No server is matching with your request\n')
    
    def find_ip(self, channel,ip):
        self.s.send('PRIVMSG ' + channel + ' :Query database [...]\n')
        self.statistic.execute("SELECT server_id,server_ip FROM servers_list")
        servers = self.statistic.fetchall()
        num = 0
        results = 0
        while (num < len(servers)):
            f_ip = servers[num][1]
            if f_ip in ip:
                self.statistic.execute("SELECT query_name,query_map,query_gametype,query_players,query_publicslots FROM querys_list WHERE query_serverid='" + str(servers[num][0]) + "'")
                server_info = self.statistic.fetchone()
                sip = str(servers[num][1])
                sname = str(server_info[0])
                sname = self.farbreplace(sname)
                smap = str(server_info[1])
                gtype = str(server_info[2])
                gtype = str(self.gametype(gtype))
                sslots = str(server_info[3])
                smaxplayer = str(server_info[4])
                self.s.send('PRIVMSG ' + channel + ' :' + sip + " - " + sname + " - " + smap + " - " + gtype + " | " + sslots + '/' + smaxplayer + '\n')
                results = results + 1
                sleep(2)
                if int(results) == 5:
                    self.s.send('PRIVMSG ' + channel + ' :At least 5 servers [...]\n')
                    break
            num = num + 1
        if (0 < results < 5):
            self.s.send('PRIVMSG ' + channel + ' :End of list [...]\n')
        if results == 0:
            self.s.send('PRIVMSG ' + channel + ' :No server is matching with your request\n')
    
    def run(self):
        self.stop = False
        textcounter = 0
        stop = 0
        result = 0
        spamnum = 0
        tsec = 0
        LOGchans=''
        LOGchansold=''
        LOGhost=''
        
        op={}
        chanusers={}

	#self.s.setsockopt(socket.SOL_SOCKET,IN.SO_BINDTODEVICE,struct.pack("%ds" % (len("eth0.1")+1,), "eth0.1"))
        self.s.bind(("178.79.142.114",0))
        self.s.connect((self.host, self.port))
        self.s.send("NICK %s\r\n" % self.nick)
        self.s.send("USER %s %s bla :%s\r\n" % (self.identt, self.host, self.realname))

        self.cursor.execute("SELECT channel FROM 1_peng_bots WHERE id='" + self.botID + "' ORDER BY channel")
        peng = self.cursor.fetchall()
        if len(peng) > 0:
            lenge=0
            while(lenge < len(peng)):
                chanusers[peng[lenge][0]]=[]
                op[peng[lenge][0]] = chanusers[peng[lenge][0]]
                lenge = lenge + 1
        print op
                        
        print "trying to connect to %s:%s" % (self.host, self.port)
        sleep(2)
        
        while True:
            if self.useprint:
                try:
                    irctext = self.s.recv(4096).split('\n')
                    textcounter = 0
                    print irctext
                    if self.stop == True:
                        self.s.close()
                        break
                        
                    while(textcounter < len(irctext)):
                        text = irctext[textcounter]
                        if len(text) > 0:
                            print text
                        data = text.split()
                        textcounter = textcounter + 1
                        if len(data) <= 1:
                            data = ['', '']
                        if data[1] == "513" and len(data) >= 9:
                            self.s.send('PONG ' + data[8] + '\n')
                        if "PING" in text and len(data) >= 2:
                            self.s.send('PONG ' + data[1] + '\n')
                        
                        self.getall = ctime()
                        self.getall = self.getall.split()
                        self.getday = self.getall[2]
                        self.getday = self.normalize_day(self.getday) # Function
                        self.getmonth = self.getall[1]
                        self.getmonth = self.getmonth.replace("Jan", "01")
                        self.getmonth = self.getmonth.replace("Feb", "02")
                        self.getmonth = self.getmonth.replace("Mar", "03")
                        self.getmonth = self.getmonth.replace("Apr", "04")
                        self.getmonth = self.getmonth.replace("May", "05")
                        self.getmonth = self.getmonth.replace("Jun", "06")
                        self.getmonth = self.getmonth.replace("Jul", "07")
                        self.getmonth = self.getmonth.replace("Aug", "08")
                        self.getmonth = self.getmonth.replace("Sep", "09")
                        self.getmonth = self.getmonth.replace("Oct", "10")
                        self.getmonth = self.getmonth.replace("Nov", "11")
                        self.getmonth = self.getmonth.replace("Dec", "12")
                        self.getdate = self.getday + "." + self.getmonth + "." + self.getall[4]
                        self.gettime = self.getall[3]
                        self.gettime = self.gettime.split(":")
                        self.gettime = self.gettime[0] + ":" + self.gettime[1] + ":" + self.gettime[2]
                         
			if "(re)connect too fast" in text:
                            MasterThread.reportThreadStatus(self.botNum)
                            self.s.close()
                            self.stop = True
                            break
                          
                        if "/MOTD" in text:
                            authing = self.botauth()
                            self.s.send ( 'PRIVMSG Q@CServe.quakenet.org :AUTH ' + authing + '\n')
                            sleep(1)
                            #self.s.send ( 'MODE ' +self.nick + ' :+x \n')
                            self.s.send("JOIN %s \r\n" % (priv_chan));
                            self.s.send("JOIN %s \r\n" % (pub_chan));
            
                        if data[1] == "QUIT":
                            getnick = data[0].split("!")
                            nick = getnick[0].replace(":","")
                            nick = nick.replace("\'","`")
                            self.peng_quit(nick) #Function
                    ##########
                    #NICK/MODE
                    ##########
                        if data[1] == "NICK" and len(data) >= 3:
                            getnick = data[0].split("!")
                            nick = getnick[0].replace(":","")
                            newnick = data[2].replace(":","")
                            chans = op.keys()
                            num = 0
                            while(num < len(chans)):
                                if nick in chanusers[chans[num]]:
                                    chanusers[chans[num]].remove(nick)
                                    chanusers[chans[num]].append(newnick)
                                    self.cursor.execute("UPDATE 1_peng_chanstats SET name='" + str(newnick) + "' WHERE name='" + nick + "' AND channel='" + chans[num] + "'")##
                                    self.cursor.execute("UPDATE 1_peng_auth SET nick='" + str(newnick) + "' WHERE nick='" + nick + "'")
                                num = num + 1
                            self.cursor.execute("UPDATE 1_peng_player SET name='" + str(newnick) + "' WHERE name='" + nick + "'")
                            print op
            
                        if data[1] == "QUIT":
                            getnick = data[0].split("!")
                            nick = getnick[0].replace(":","")
                            nick = nick.replace("\'","`")
                            chans = op.keys()
                            num = 0
                            while(num < len(chans)):
                                if nick in chanusers[chans[num]]:
                                    chanusers[chans[num]].remove(nick)
                                num = num + 1
                            self.cursor.execute("DELETE from 1_peng_auth WHERE Nick='" + str(nick) + "'")
                            print op
            
                        if data[1] == "MODE" and len(data) >= 5:
                            if "+o" in data[3]:
                                if data[2] in op.keys():
                                    chanusers[data[2]].append(data[4])
                                    self.cursor.execute("SELECT * FROM 1_peng_chanstats WHERE name='" + data[4] + "' AND channel='" + data[2] + "'") ##
                                    LOGexist = self.cursor.fetchone()##
                                    if LOGexist == None:##
                                        self.cursor.execute("INSERT INTO 1_peng_chanstats (channel, name, qauth, lastseen, host) VALUES ('" + data[2] + "', '" + data[4] + "', '','','')")##
                                    self.s.send('WHOIS ' + data[4] + '\n')##
                            elif "-o" in data[3]:
                                if data[2] in op.keys():
                                    if data[4] in op.values():
                                        chanusers[data[2]].remove(data[4])
                            print op
            
                    ##########
                    #OPlist
                    ##########
                        if data[1] == "353" and len(data) >= 5:
                            if data[4] in op.keys():
                                replacer = data[0] + " " + data[1] + " " + data[2] + " " + data[3] + " " + data[4] + " :"
                                getnames = text.replace(replacer, "")
                                getnames = getnames.split()
                                zahl = 0
                                names = ""
                                while(zahl < len(getnames)):
                                    if "@" in getnames[zahl]:
                                        getnames[zahl] = getnames[zahl].replace("@", "")
                                        chanusers[data[4]].append(getnames[zahl])
                                        if getnames[zahl] != "Q":##
                                            self.cursor.execute("SELECT * FROM 1_peng_chanstats WHERE name='" + getnames[zahl] + "' AND channel='" + data[4] + "'")##
                                            LOGexist = self.cursor.fetchone()##
                                            if LOGexist == None:##
                                                self.cursor.execute("INSERT INTO 1_peng_chanstats (channel, name, qauth, lastseen, host) VALUES ('" + data[4] + "', '" + getnames[zahl] + "', '','','')")##
                                            self.cursor.execute("SELECT authnick,host FROM 1_peng_auth WHERE nick='" + getnames[zahl] + "'")##
                                            is_authedcheck = self.cursor.fetchone()##
                                            if is_authedcheck == None:##
                                                self.s.send('WHOIS ' + getnames[zahl] + '\n')##
                                            else:
                                                self.cursor.execute("UPDATE 1_peng_chanstats SET qauth='" + str(is_authedcheck[0]) + "' WHERE name='" + getnames[zahl] + "'")##
                                                self.cursor.execute("UPDATE 1_peng_chanstats SET host='" + str(is_authedcheck[1]) + "' WHERE name='" + getnames[zahl] + "'")##
                                                self.cursor.execute("UPDATE 1_peng_chanstats SET lastseen='" + str(self.getdate) + " " + str(self.gettime) + "' WHERE name='" + getnames[zahl] + "'")##
                                    zahl = zahl + 1
#                                if len(chanusers[data[4]]) <= 1:
#                                    self.s.send('PRIVMSG ' + priv_chan + ' :One or less ops in ' + data[4] + '\n')
#                                    sleep(2)
                                print op
                                
                    ##########
                    #Auther
                    ##########
                        if data[1] == "311" and len(data) >= 6:##
                            LOGhost = data[5]##
                            
                        if data[1] == "319" and len(data) >= 4:##
                            replacer = data[0] + ' ' + data[1] + ' ' + data[2] + ' ' + data[3] + ' :'##
                            LOGchans = text.replace(replacer,'')##
                            LOGchans = LOGchans.replace("@", "")##
                            LOGchans = LOGchans.replace("+", "")##
                            LOGchans = LOGchans.replace("'", "`")##
                                
                        if data[1] == "330" and len(data) >= 5:
                            nick = data[3]
                            if nick != "Q":
                                authnick = data[4]
                                self.cursor.execute("SELECT * FROM 1_peng_auth WHERE Nick='" + nick + "'")
                                getauth = self.cursor.fetchone()
                                if getauth == None:
                                    self.cursor.execute("INSERT INTO 1_peng_auth (Nick, AuthNick, host) VALUES ('" + nick + "', '" + authnick + "', '" + LOGhost + "')")
            
                                if LOGchans != LOGchansold:##
                                    LOGchansold = LOGchans##
                                    num = 0##
                                    LOGchans = LOGchans.split()##
                                    while (num < len(LOGchans)):##
                                        self.cursor.execute("SELECT name FROM 1_peng_chanstats WHERE name='" + nick + "' AND channel='" + LOGchans[num] + "'")##
                                        LOGexist = self.cursor.fetchone()##
                                        if LOGexist == None:##
                                            self.cursor.execute("UPDATE 1_peng_chanstats SET qauth='" + str(authnick) + "' WHERE name='" + nick + "'")##
                                            self.cursor.execute("UPDATE 1_peng_chanstats SET host='" + str(LOGhost) + "' WHERE name='" + nick + "'")##
                                            self.cursor.execute("UPDATE 1_peng_chanstats SET lastseen='" + str(self.getdate) + " " + str(self.gettime) + "' WHERE name='" + nick + "'")##
                                        num = num + 1##
            
                        if "PRIVMSG" in text and len(data) >= 4:
                            getnick = data[0].split("!")
                            nick = getnick[0].replace(":","")
                            nick = nick.replace("\'","`")

                            if data[3] == ":!restartmaster":
                                host = getnick[1]
                                if host in OWNER:
                                    if self.botID == "001":
                                        masterThread.start()
                                        
                            if data[3] == ":!die":
                                host = getnick[1]
                                if host in OWNER:
                                    if len(data) == 5:
                                        if data[4] == self.botID:
                                            self.s.send('QUIT\n')
                                            self.s.close()

			    if data[3] == ":!myport":
				self.s.send('PRIVMSG ' + priv_chan + ' :' + str(self.port) + '\n')

                            if data[3] == ":!restart":
                                host = getnick[1]
                                if host in OWNER:
                                    if len(data) == 5:
                                        if data[4] == self.botID:
                                            self.s.send('QUIT\n')
                                            self.s.close()
                                            threads[self.botID].close()
                                            threads[self.botID].start()
                                        
                    ##########
                    #SPAMING
                    ##########
                            #SPAM
                            if data[3] == (":" + sup_spam):
                                channel = data[2]
                                if channel == "#peng.ubber.priv":
                                    if len(data) == 6:
                                        if data[5].isdigit() == True:
                                            if data[4] == "RINGER":
                                                self.spam_match(data,channel,"ringer") #Function
                                            if data[4] == "RECRUIT":
                                                self.spam_match(data,channel,"recruit") #Function
                                            if data[4] == "PCW":
                                                self.spam_match(data,channel,"pcw") #Function
                                            if data[4] == "CW":
                                                self.spam_match(data,channel,"cw") #Function
                                            if data[4] == "MSG":
                                                self.spam_match(data,channel,"msg") #Function
                                            if data[4] == "GTV":
                                                self.spam_match(data,channel,"gtv") #Function
                                            if data[4] == "AMSG":
                                                self.spam_match(data,channel,"amsg") #Function
                                        
                    ##########
                    #JOINING
                    ##########
                            #JOIN
                            if data[3] == (":" + sup_join):
                                channel = data[2]
                                if channel == "#peng.ubber.priv":
                                    if len(data) == 5:
                                        if data[4] == self.nick:
                                            self.cursor.execute("SELECT channel FROM 1_peng_bots WHERE id='" + self.botID + "'")
                                            peng = self.cursor.fetchall()
                                            if len(peng) > 0:
                                                lenge = 0
                                                while(lenge < len(peng)):
                                                    self.s.send('JOIN ' + peng[lenge][0] + '\n')
                                                    lenge = lenge + 1
                                    if len(data) == 6:
                                        if data[4] == self.nick:
                                            chanusers[data[5]]=[]
                                            op[data[5]] = chanusers[data[5]]  
                                            print op
                                            self.s.send('JOIN ' + data[5] + '\n')
            
                            #REMOVE
                            if data[3] == (":" + sup_remove):
                                channel = data[2]
                                if channel == "#peng.ubber.priv":
                                    if len(data) == 6:
                                        if data[4] == self.nick:
                                            self.s.send('PART ' + data[5] + '\n')
                                            if data[5] in op.keys():
                                                op.pop(data[5])
                                            self.s.send('PRIVMSG ' + channel + ' :#PARTED#\n')
                                                                                    
                    ##########
                    #DISPLAY
                    ##########
                            #PCW
                            if data[3] == (":" + cmd_prefix + show_pcw):
                                channel = data[2]
                                if channel in op.keys():
                                    opchan = op[channel] #Function
                                    if nick in opchan:
                                        authed = self.check_auth(nick) #Function
                                        if authed == True:
                                            self.set_display(data,channel,"pcw")
                                        else:
                                            self.s.send('NOTICE ' + nick + ' :' + not_auth + '\n')
                                    else:
                                        self.s.send('NOTICE ' + nick + ' :' + not_oped + '\n')
            
                            #CW
                            if data[3] == (":" + cmd_prefix + show_cw):
                                channel = data[2]
                                if channel in op.keys():
                                    opchan = op[channel] #Function
                                    if nick in opchan:
                                        authed = self.check_auth(nick) #Function
                                        if authed == True:
                                            self.set_display(data,channel,"cw")
                                        else:
                                            self.s.send('NOTICE ' + nick + ' :' + not_auth + '\n')
                                    else:
                                        self.s.send('NOTICE ' + nick + ' :' + not_oped + '\n')
            
                            #RINGER
                            if data[3] == (":" + cmd_prefix + show_ringer):
                                channel = data[2]
                                if channel in op.keys():
                                    opchan = op[channel] #Function
                                    if nick in opchan:
                                        authed = self.check_auth(nick) #Function
                                        if authed == True:
                                            self.set_display(data,channel,"ringer")
                                        else:
                                            self.s.send('NOTICE ' + nick + ' :' + not_auth + '\n')
                                    else:
                                        self.s.send('NOTICE ' + nick + ' :' + not_oped + '\n')
            
                            #RECRUIT
                            if data[3] == (":" + cmd_prefix + show_recruit):
                                channel = data[2]
                                if channel in op.keys():
                                    opchan = op[channel] #Function
                                    if nick in opchan:
                                        authed = self.check_auth(nick) #Function
                                        if authed == True:
                                            self.set_display(data,channel,"recruit")
                                        else:
                                            self.s.send('NOTICE ' + nick + ' :' + not_auth + '\n')
                                    else:
                                        self.s.send('NOTICE ' + nick + ' :' + not_oped + '\n')
            
                            #MSG
                            if data[3] == (":" + cmd_prefix + show_msg):
                                channel = data[2]
                                if channel in op.keys():
                                    opchan = op[channel] #Function
                                    if nick in opchan:
                                        authed = self.check_auth(nick) #Function
                                        if authed == True:
                                            self.set_display(data,channel,"msg")
                                        else:
                                            self.s.send('NOTICE ' + nick + ' :' + not_auth + '\n')
                                    else:
                                        self.s.send('NOTICE ' + nick + ' :' + not_oped + '\n')
            
                            #GTV
                            if data[3] == (":" + cmd_prefix + show_gtv):
                                channel = data[2]
                                if channel in op.keys():
                                    opchan = op[channel] #Function
                                    if nick in opchan:
                                        authed = self.check_auth(nick) #Function
                                        if authed == True:
                                            self.set_display(data,channel,"gtv")
                                        else:
                                            self.s.send('NOTICE ' + nick + ' :' + not_auth + '\n')
                                    else:
                                        self.s.send('NOTICE ' + nick + ' :' + not_oped + '\n')
            
                            #PICKUP
                            if data[3] == (":" + cmd_prefix + enable_pickup):
                                channel = data[2]
                                if channel in op.keys():
                                    opchan = op[channel] #Function
                                    if nick in opchan:
                                        authed = self.check_auth(nick) #Function
                                        if authed == True:
                                            self.set_display(data,channel,"pickup")
                                        else:
                                            self.s.send('NOTICE ' + nick + ' :' + not_auth + '\n')
                                    else:
                                        self.s.send('NOTICE ' + nick + ' :' + not_oped + '\n')
                                        
                    ##########
                    #STATUS
                    ##########
                            #STATUS
                            if data[3] == (":" + cmd_prefix + show_status):
                                channel = data[2]
                                if channel in op.keys():
                                    opchan = op[channel] #Function
                                    if nick in opchan:
                                        authed = self.check_auth(nick) #Function
                                        if authed == True:
                                            self.cursor.execute("SELECT pcw,cw,ringer,msg,recruit,gtv,ablemsg,ablegtv,pickup FROM 1_peng_bots WHERE id='" + self.botID + "' AND channel='" + channel + "'")
                                            peng = self.cursor.fetchone()
                                            peng_pcw = peng[0]
                                            peng_cw = peng[1]
                                            peng_ringer = peng[2]
                                            peng_msg = peng[3]
                                            peng_recruit = peng[4]
                                            peng_gtv = peng[5]
                                            peng_smsg = peng[6]
                                            peng_sgtv = peng[7]
                                            peng_spickup = peng[8]
                                            self.s.send('PRIVMSG ' + channel + ' :[STATUS] Displaypcw: ' + peng_pcw + ' | Displaycw: ' + peng_cw + ' | Displayringer: ' + peng_ringer + ' | Displayrecruit: ' + peng_recruit + ' | Displaymsg: ' + peng_msg + ' | Displaygtv: ' + peng_gtv + ' | Displaypickup: ' + peng_spickup + ' | Submitmsg: ' + peng_smsg + ' | Submitgtv: ' + peng_sgtv + '\n')
                                        else:
                                            self.s.send('NOTICE ' + nick + ' :' + not_auth + '\n')
                                    else:
                                        self.s.send('NOTICE ' + nick + ' :' + not_oped + '\n')
                                        
                            if data[3] == (":" + cmd_prefix + pickup_help):
                                channel = data[2]
                                self.peng_help(channel,nick) #Function                    
            
                                            
                    ##########
                    #LIST
                    ##########
                            #PCW
                            if data[3] == (":" + cmd_prefix + list_pcw):
                                channel = data[2]
                                if channel in op.keys():
                                    opchan = op[channel] #Function
                                    if nick in opchan:
                                        authed = self.check_auth(nick) #Function
                                        if authed == True:
                                            self.show_list(channel,self.gettime,"pcw") #Function
                                        else:
                                            self.s.send('NOTICE ' + nick + ' :' + not_auth + '\n')
                                    else:
                                        self.s.send('NOTICE ' + nick + ' :' + not_oped + '\n')
                                    
                            #CW
                            if data[3] == (":" + cmd_prefix + list_cw):
                                channel = data[2]
                                if channel in op.keys():
                                    opchan = op[channel] #Function
                                    if nick in opchan:
                                        authed = self.check_auth(nick) #Function
                                        if authed == True:
                                            self.show_list(channel,self.gettime,"cw") #Function
                                        else:
                                            self.s.send('NOTICE ' + nick + ' :' + not_auth + '\n')
                                    else:
                                        self.s.send('NOTICE ' + nick + ' :' + not_oped + '\n')
                                    
                            #Ringer
                            if data[3] == (":" + cmd_prefix + list_ringer):
                                channel = data[2]
                                if channel in op.keys():
                                    opchan = op[channel] #Function
                                    if nick in opchan:
                                        authed = self.check_auth(nick) #Function
                                        if authed == True:
                                            self.show_list(channel,self.gettime,"ringer") #Function
                                        else:
                                            self.s.send('NOTICE ' + nick + ' :' + not_auth + '\n')
                                    else:
                                        self.s.send('NOTICE ' + nick + ' :' + not_oped + '\n')
                                    
                            #Recruit
                            if data[3] == (":" + cmd_prefix + list_recruit):
                                channel = data[2]
                                if channel in op.keys():
                                    opchan = op[channel] #Function
                                    if nick in opchan:
                                        authed = self.check_auth(nick) #Function
                                        if authed == True:
                                            self.show_list(channel,self.gettime,"recruit") #Function
                                        else:
                                            self.s.send('NOTICE ' + nick + ' :' + not_auth + '\n')
                                    else:
                                        self.s.send('NOTICE ' + nick + ' :' + not_oped + '\n')
                                    
                            #MSG
                            if data[3] == (":" + cmd_prefix + list_msg):
                                channel = data[2]
                                if channel in op.keys():
                                    opchan = op[channel] #Function
                                    if nick in opchan:
                                        authed = self.check_auth(nick) #Function
                                        if authed == True:
                                            self.show_list(channel,self.gettime,"msg") #Function
                                        else:
                                            self.s.send('NOTICE ' + nick + ' :' + not_auth + '\n')
                                    else:
                                        self.s.send('NOTICE ' + nick + ' :' + not_oped + '\n')
                                        
                            #GTV
                            if data[3] == (":" + cmd_prefix + list_gtv):
                                channel = data[2]
                                if channel in op.keys():
                                    opchan = op[channel] #Function
                                    if nick in opchan:
                                        authed = self.check_auth(nick) #Function
                                        if authed == True:
                                            self.show_list(channel,self.gettime,"gtv") #Function
                                        else:
                                            self.s.send('NOTICE ' + nick + ' :' + not_auth + '\n')
                                    else:
                                        self.s.send('NOTICE ' + nick + ' :' + not_oped + '\n')
                                    
                    ##########
                    #SUMBIT
                    ##########
                            #PCW
                            if data[3] == (":" + cmd_prefix + submit_pcw):
                                channel = data[2]
                                if channel in op.keys():
                                    opchan = op[channel] #Function
                                    if nick in opchan:
                                        authed = self.check_auth(nick) #Function
                                        if authed == True:
                                            banned = self.check_ban(nick) #Function
                                            if banned == False:
                                                able = self.flood_prot(channel,nick,"PCW") #Function
                                                if able == True:
                                                    self.submit_match(nick,data,channel,"PCW")
                                            else:
                                                self.s.send('PRIVMSG ' + channel + ' :' + is_banned + '\n')
                                        else:
                                            self.s.send('NOTICE ' + nick + ' :' + not_auth + '\n')
                                    else:
                                        self.s.send('PRIVMSG ' + channel + ' :' + not_oped + '\n')
            
                            #CW
                            if data[3] == (":" + cmd_prefix + submit_cw):
                                channel = data[2]
                                if channel in op.keys():
                                    opchan = op[channel] #Function
                                    if nick in opchan:
                                        authed = self.check_auth(nick) #Function
                                        if authed == True:
                                            banned = self.check_ban(nick) #Function
                                            if banned == False:
                                                able = self.flood_prot(channel,nick,"CW") #Function
                                                if able == True:
                                                    self.submit_match(nick,data,channel,"CW")
                                            else:
                                                self.s.send('PRIVMSG ' + channel + ' :' + is_banned + '\n')
                                        else:
                                            self.s.send('NOTICE ' + nick + ' :' + not_auth + '\n')
                                    else:
                                        self.s.send('PRIVMSG ' + channel + ' :' + not_oped + '\n')
                                    
                            #RINGER
                            if data[3] == (":" + cmd_prefix + submit_ringer):
                                channel = data[2]
                                if channel in op.keys():
                                    opchan = op[channel] #Function
                                    if nick in opchan:
                                        authed = self.check_auth(nick) #Function
                                        if authed == True:
                                            banned = self.check_ban(nick) #Function
                                            if banned == False:
                                                able = self.flood_prot(channel,nick,"RINGER") #Function
                                                if able == True:
                                                    self.submit_match(nick,data,channel,"RINGER")
                                            else:
                                                self.s.send('PRIVMSG ' + channel + ' :' + is_banned + '\n')
                                        else:
                                            self.s.send('NOTICE ' + nick + ' :' + not_auth + '\n')
                                    else:
                                        self.s.send('PRIVMSG ' + channel + ' :' + not_oped + '\n')
                                    
                            #RECRUIT
                            if data[3] == (":" + cmd_prefix + submit_recruit):
                                channel = data[2]
                                if channel in op.keys():
                                    opchan = op[channel] #Function
                                    if nick in opchan:
                                        authed = self.check_auth(nick) #Function
                                        if authed == True:
                                            banned = self.check_ban(nick) #Function
                                            if banned == False:
                                                able = self.flood_prot(channel,nick,"RECRUIT") #Function
                                                if able == True:
                                                    self.submit_match(nick,data,channel,"RECRUIT")
                                            else:
                                                self.s.send('PRIVMSG ' + channel + ' :' + is_banned + '\n')
                                        else:
                                            self.s.send('NOTICE ' + nick + ' :' + not_auth + '\n')
                                    else:
                                        self.s.send('PRIVMSG ' + channel + ' :' + not_oped + '\n')
            
                            #MSG
                            if data[3] == (":" + cmd_prefix + submit_msg):
                                channel = data[2]
                                if channel in op.keys():
                                    opchan = op[channel] #Function
                                    if nick in opchan:
                                        authed = self.check_auth(nick) #Function
                                        if authed == True:
                                            banned = self.check_ban(nick) #Function
                                            if banned == False:
                                                self.cursor.execute("SELECT channel FROM 1_peng_bots WHERE ablemsg='on' AND channel='" + channel + "' AND ID='" + self.botID + "'")
                                                access = self.cursor.fetchone()
                                                if not access == None:
                                                    able = self.flood_prot(channel,nick,"MSG") #Function
                                                    if able == True:
                                                        self.submit_match(nick,data,channel,"MSG")
                                                else:
                                                    self.s.send('PRIVMSG ' + channel + ' :' + no_access_msg + '\n')
                                            else:
                                                self.s.send('PRIVMSG ' + channel + ' :' + is_banned + '\n')
                                        else:
                                            self.s.send('NOTICE ' + nick + ' :' + not_auth + '\n')
                                    else:
                                        self.s.send('PRIVMSG ' + channel + ' :' + not_oped + '\n')
            
                            #GTV
                            if data[3] == (":" + cmd_prefix + submit_gtv):
                                channel = data[2]
                                if channel in op.keys():
                                    opchan = op[channel] #Function
                                    if nick in opchan:
                                        authed = self.check_auth(nick) #Function
                                        if authed == True:
                                            banned = self.check_ban(nick) #Function
                                            if banned == False:
                                                self.cursor.execute("SELECT channel FROM 1_peng_bots WHERE ablegtv='on' AND channel='" + channel + "' AND ID='" + self.botID + "'")
                                                access = self.cursor.fetchone()
                                                if not access == None:
                                                    able = self.flood_prot(channel,nick,"GTV") #Function
                                                    if able == True:
                                                        self.submit_match(nick,data,channel,"GTV")
                                                else:
                                                    self.s.send('PRIVMSG ' + channel + ' :' + no_access_gtv + '\n')
                                            else:
                                                self.s.send('PRIVMSG ' + channel + ' :' + is_banned + '\n')
                                        else:
                                            self.s.send('NOTICE ' + nick + ' :' + not_auth + '\n')
                                    else:
                                        self.s.send('PRIVMSG ' + channel + ' :' + not_oped + '\n')
                                    
                    ##########
                    #PICKUP
                    ##########
                        #MSGS
                            if data[3] == (":" + info_gameover):
                                channel = data[2]
                                if channel == "#peng.ubber.priv":
                                    if len(data) > 4:
                                        self.peng_spam(data[4],'gameover',channel) #Function
                            if data[3] == (":" + info_datasent):
                                channel = data[2]
                                if channel == "#peng.ubber.priv":
                                    if len(data) == 4:
                                        self.peng_spam(nick,'datasent',channel) #Function
                            if data[3] == (":" + info_signup):
                                channel = data[2]
                                if channel == "#peng.ubber.priv":
                                    if len(data) == 4:
                                        self.peng_spam(nick,'signup',channel) #Function
                            if data[3] == (":" + info_pm):
                                channel = data[2]
                                if channel == "#peng.ubber.priv":
                                    if len(data) == 4:
                                        self.peng_pm() #Function
                                    
                        #CMDS  
                            if data[3] == (":" + cmd_prefix + pickup_prefix):
                                channel = data[2]
                                if len(data) > 4:
                                    if channel in op.keys():
                                        locked = self.peng_lock() #Function
                                        if locked == False:
                                            enabled = self.peng_enable(channel) #Function
                                            if enabled == True:
                                                authed = self.check_auth(nick) #Function
                                                if authed == True:
                                                    game_started = self.peng_gamestarted() #Function
                                                    if game_started == False and (data[4] != pickup_pw and data[4] != pickup_gameover):
                                            #ADD
                                                        if data[4] == pickup_add:
                                                            self.peng_add(channel,nick) #Function
                                            #REMOVE
                                                        if data[4] == pickup_remove:
                                                            self.peng_remove(channel,nick) #Function
                                            #MAPS
                                                        if data[4] == pickup_maps:
                                                            self.peng_maps(channel) #Function
                                            #MODES
                                                        if data[4] == pickup_modes:
                                                            self.peng_modes(channel) #Function
                                            #VOTE
                                                        if data[4] == pickup_vote:
                                                            self.peng_vote(channel,nick,data,text) #Function
                                            #HELP
                                                        if data[4] == pickup_help:
                                                            self.peng_help(channel) #Function
                                            #STATUS
                                                        if data[4] == pickup_status:
                                                            self.peng_status(channel) #Function
                                            #PLAYERS
                                                        if data[4] == pickup_players:
                                                            self.peng_players(channel,nick) #Function
                                                            
                                                    elif game_started == True and (data[4] == pickup_pw or data[4] == pickup_gameover):
                                            #GAMEOVER
                                                        if data[4] == pickup_gameover:
                                                            self.peng_gameover(channel,nick) #Function
                                            #PW
                                                        if data[4] == pickup_pw:
                                                            self.peng_pw(nick,channel) #Function
                                                            
                                                    elif game_started == True and (data[4] != pickup_pw or data[4] != pickup_gameover):
                                                        self.cursor.execute("SELECT status FROM 1_peng_status WHERE name='endtime'")
                                                        nextgame_all = self.cursor.fetchone()
                                                        nextgame_all = nextgame_all[0]
                                                        nextgame = str(nextgame_all[8]) + str(nextgame_all[9]) + ":" + str(nextgame_all[10]) + str(nextgame_all[11]) + ":" + str(nextgame_all[12]) + str(nextgame_all[13])
                                                        pkup_started_mod = pkup_started.replace(".time.", nextgame)
                                                        self.s.send('PRIVMSG ' + channel + ' :' + pkup_started_mod + '\n')
                                                       
                                                    elif game_started == False and (data[4] == pickup_pw or data[4] == pickup_gameover):
                                                        self.s.send('NOTICE ' + nick + ' :' + not_added + '\n')
                                                else:
                                                    self.s.send('NOTICE ' + nick + ' :' + not_auth + '\n')
                                            else:
                                                self.s.send('PRIVMSG ' + channel + ' :' + pkup_nchan + '\n')
                                        else:
                                            self.s.send('PRIVMSG ' + channel + ' :' + pkup_lock  + '\n')
                                else:
                                    self.s.send('PRIVMSG ' + channel + ' :' + pkup_para + '\n')
            
                    ###########
                    #SERVERFIND
                    ###########
                            if data[3] == (":" + cmd_prefix + finder_prefix):
                                channel = data[2]
                                if channel in op.keys():
                                    opchan = op[channel] #Function
                                    if nick in opchan:
                                        authed = self.check_auth(nick) #Function
                                        if authed == True:
                                            banned = self.check_ban(nick) #Function
                                            if banned == False:
                                                if len(data) != 6:
                                                    self.s.send('PRIVMSG ' + channel + ' :Missing playername. ' + cmd_prefix + ' ' + finder_prefix + ' <' + finder_player + '/' + finder_name + '/' + finder_ip + '> <searchtag>\n')
                                                else:
                                                    if data[4] == finder_player:
                                                        self.find_player(channel,data[4]) #Function
                                                    elif data[4] == finder_name:
                                                        self.find_name(channel,data[5]) #Function
                                                    elif data[4] == finder_ip:
                                                        if not ":" in data[5]:
                                                            data_ip = data[5] + ":27960"
                                                        else:
                                                            data_ip = data[5]
                                                        self.find_ip(channel,data_ip) #Function

                except:
                    text=text.replace("'","_`_")
                    typ = str(sys.exc_info()[1]).replace("'","_`_")
                    self.cursor.execute("INSERT INTO `1_peng_error` (`bot`,`text`,`type`,`time`) VALUES ('" + str(self.botID) +"', '" + str(text) +"', '" + str(typ) + "', '" + str(self.getdate) + " " + str(self.gettime) + "')")
                    self.s.close()
                    print "DIE"
                    traceback.print_exc(file=sys.stdout)
                    sys.exit()                    
            else:
                sleep(3)              
##[END - PengBot Class]##

##[BEGIN - Main Code]##
masterThread = botMaster(1)
masterThread.start()

#threads[24] = botPeng("024",1)
#threads[24].start()
##[END - Main Code]##
