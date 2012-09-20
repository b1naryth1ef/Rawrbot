import socket
import string
import MySQLdb
import urllib
from time import ctime
from time import sleep

IP="irc.quakenet.org"
PORT=6667
NICK="UrT-TV-Bot"
IDENT="GTV-Bot"
REALNAME="GTV-Bot"
text=""
channel="#urt-tv"
OWNER="~gost0r@Gost0r.users.quakenet.org Liquid@pengbot.de"
admins="~gost0r ~Azle_ ~Liq``"

#ts3ip = "62.75.246.191:9991"

stop = 0
result = 0
spamnum = 0
tsec = 0

#############[FUNCTION]##############

def check_timeout(time,tset):
    global tsec
    if tset == 1:
        gethour = int(time[0]) * 3600
        getmin = int(time[1]) * 60
        tsec = gethour + getmin + int(time[2])
        tsec = tsec + 300
    if tset == 0:
        gethour = int(gettime[0]) * 3600
        getmin = int(gettime[1]) * 60
        tnow = gethour + getmin + int(time[2])
        if tsec <= tnow:
            reconnect()

def normalize_day(day):
    if len(day) == 1:
        return "0" + day
    else:
        return day

def reconnect():
    print "RECONNECT"
    irc.close()
    sleep(30)
    #irc = socket.socket ( socket.AF_INET, socket.SOCK_STREAM )
    #irc.bind(("178.79.142.114",0))
    irc.connect ( ( IP, PORT ) )
    irc.send ( 'USER  ' + IDENT + ' ' + IDENT + ' bla : ' + REALNAME + '\n' )
    irc.send ( 'NICK ' + NICK + '\n')

##[UPDATE]###################################################################################
update = 0
getdate = 0
def deleter(foldate,getdate):
    cursor.execute("SELECT Date,ID FROM gtv_sc WHERE Done='no' AND Public='no'")
    uz = cursor.fetchall()
    stop = 0
    num = 0
    while(stop < 1):
        if num < len(uz):
            uz1 = uz[num]
            sgetdate = getdate.split(".")
            sgetdate = sgetdate[2] + sgetdate[1] + sgetdate[0]
            uzdate = uz1[0].split(".")
            uzdate = uzdate[2] + uzdate[1] + uzdate[0]
            if int(uzdate) < int(sgetdate):
                cursor.execute("DELETE from gtv_sc WHERE ID='" + str(uz1[1]) + "'")
        else:
            stop = 1
        num = num + 1

##############################################################################################

irc = socket.socket ( socket.AF_INET, socket.SOCK_STREAM )
irc.bind(("178.79.142.114",0))
irc.connect ( ( IP, PORT ) )
irc.send ( 'USER  ' + IDENT + ' ' + IDENT + ' bla : ' + REALNAME + '\n' )
irc.send ( 'NICK ' + NICK + '\n')

mysql = MySQLdb.connect (host = "localhost",
                         user = "1_pengbotuser",
                         passwd = "L0k0m0tive",
                         db = "1_urt-tv")
cursor = mysql.cursor()

while True:
    try:
        text = irc.recv(4096)
        print text
        data = text.split()

        if len(data) <= 0:
            data = ['']

        if data[0] == "ERROR":
            reconnect()

        getall = ctime()
        getall = getall.split()
        getday = getall[2]
        getday = normalize_day(getday) # Function
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
        upgetdate = getdate
        getdate = getday + "." + getmonth + "." + getall[4]
        gettime = getall[3]
        sgettime = gettime.split(":")
        gettime = sgettime[0] + ":" + sgettime[1]

        folday = int(getday) + 1
        folday = normalize_day(str(folday)) # Function
        if getmonth == "01" or getmonth == "03" or getmonth == "05" or getmonth == "07" or getmonth == "08" or getmonth == "10" or getmonth == "12":
            if int(folday) > 31:
                if getmonth == "12":
                    folmonth = "01"
                    getyear = int(getall[4]) + 1
                    foldate = str(folday) + "." + str(getmonth) + "." + str(getyear)
                else:
                    folday = "01"
                    getmonth = int(getmonth) + 1
                    foldate = str(folday) + "." + str(getmonth) + "." + str(getall[4])
        if int(folday) > 31:
            folday = "01"
            getmonth = int(getmonth) + 1
            foldate = str(folday) + "." + str(getmonth) + "." + str(getall[4])
        foldate = ['','']
        foldate = [foldate, getdate]

        if data[1] == "513":
            irc.send('PONG ' + data[8] + '\n')
            check_timeout(sgettime,1)

        if "PING" in text:
            irc.send('PONG ' + data[1] + '\n')
            check_timeout(sgettime,1)
            
        if "MOTD" in text:
            irc.send ( 'PRIVMSG Q@CServe.quakenet.org :AUTH GTV-Bot 6FjL-XiXav\n')
        #    irc.send ( 'PRIVMSG Q@CServe.quakenet.org :AUTH UrT-TVbot TIv!6CjCnz\n')
            sleep(1)
            #irc.send ( 'MODE ' + NICK + ' :+x \n')
            irc.send ( 'JOIN #urt-tv\n')
            irc.send ( 'JOIN #urt-tv.admin\n')
            irc.send ( 'JOIN #urban-zone.radio uzr\n')
        #    irc.send ( 'JOIN #urt-tv.bot\n')

        if tsec == 0:
            check_timeout(sgettime,1)
        else:
            check_timeout(sgettime,0)

        #UPDATER
        uptime = gettime.split(":")
        uptime = str(uptime[0]) + str(uptime[1])
        if update == 1:
            if int(uptime) >= 1500:
                deleter(foldate,getdate)
                update = 2
        elif update == 2:
            if int(uptime) >= 1800:
                deleter(foldate,getdate)
                update = 3
        if upgetdate != getdate:
            if int(uptime) <= 1500:
                update = 1
            else:
                update = 2
            

        #AUTOSPAM#
        cursor.execute("SELECT TeamA, TeamB, Time, Server, Spam, ID, Stream, Shoutcaster FROM gtv_sc WHERE Date='" + getdate + "' AND Public='yes' AND Spam='0' OR Spam='1' ORDER BY Month,date,Time")
        gtv = cursor.fetchall()
        cursor.execute("SELECT status FROM status_new WHERE Name='ts3'")
        ts3 = cursor.fetchone()
        lengtv = len(gtv) -1
        stop = 0
        result = 0
        gtvspam = ""
        while (stop < 1):
            if lengtv >= 0:
                gtv1 = gtv[int(lengtv)]
                gtvtime = gtv1[2]
                gtvtime = gtvtime.split(":")
                if gtv1[4] == "0":
                    spamnum = "1"
                    gtvmin = int(gtvtime[1]) + 5
                    if str(gtvmin) == "5":
                        gtvmin = "05"
                    gtvtime = str(gtvtime[0]) + str(gtvmin)
                elif gtv1[4] == "1":
                    spamnum = "2"
                    gtvmin = int(gtvtime[1]) + 35
                    if gtvmin >= 60:
                        gtvmin = gtvmin - 60
                        gtvtime[0] = int(gtvtime[0]) + 1
                        if gtvmin <= 9:
                            gtvmin = "0" + str(gtvmin)
                    gtvtime = str(gtvtime[0]) + str(gtvmin)
                newtime = gettime.split(":")
                newtime = newtime[0] + newtime[1]
                if newtime >= gtvtime:
                    cursor.execute("UPDATE gtv_sc SET Spam='" + str(spamnum) + "' WHERE ID='" + str(gtv1[5]) + "'")
                    if result == 0:
                        result = 1
                        gtvspam = "!msg [GTV] Watch now! " + gtv1[0] + " vs " + gtv1[1] + " - /connect " + gtv1[3]
                        gtvspam1 = "!gtvmsg Watch now! " + gtv1[0] + " vs " + gtv1[1] + " - /connect " + gtv1[3]
                        if gtv1[6] != "":
                            gtvspam = gtvspam + " - Stream: " + gtv1[6]
                            gtvspam1 = gtvspam1 + " - Stream: " + gtv1[6]
                        if gtv1[7] != "" and gtv1[6] == "":
                            gtvspam = gtvspam + " - TS3CAST: " + ts3[0]
                            gtvspam1 = gtvspam1 + " - TS3CAST: " + ts3[0]
                    else:
                        gtvspam = gtvspam + " | " + gtv1[0] + " vs " + gtv1[1] + " - /connect " + gtv1[3]
                        gtvspam1 = gtvspam1 + " | " + gtv1[0] + " vs " + gtv1[1] + " - /connect " + gtv1[3]
                        if gtv1[6] != "":
                            gtvspam = gtvspam + " - Stream: " + gtv1[6]
                            gtvspam1 = gtvspam1 + " - Stream: " + gtv1[6]
                        if gtv1[7] != "" and gtv1[6] == "":
                            gtvspam = gtvspam + " - TS3CAST: " + ts3[0]
                            gtvspam1 = gtvspam1 + " - TS3CAST: " + ts3[0]

            else:
                stop = 1
                if result == 1:
                    print gtvspam
                    irc.send('PRIVMSG #urt-tv :' + gtvspam1 + '\n')
                    irc.send('PRIVMSG #urt-tv :' + gtvspam + '\n')
                    irc.send('PRIVMSG #urt-tv.admin :GTV spammed\n')
            lengtv = lengtv - 1

        if "PRIVMSG" in text:
            getnick = data[0].split("!")
            nick = getnick[0].replace(":","")
            nick = nick.replace("\'","`")
            
            if data[3] == ":!die":
                host = getnick[1]
                if host == OWNER:
                    irc.send('QUIT\n')
                    close

            if data[3] == ":!ts3":
                channel = data[2]
                cursor.execute("SELECT status FROM status_new WHERE Name='ts3'")
                ts3 = cursor.fetchone()
                irc.send('PRIVMSG ' + channel + ' :Ts3 IP: ' + ts3[0] + '\n')

            if data[3] == ":!gtv":
                channel = data[2]
                if "#urt-tv" in data[2]:
                    if len(data) <= 4:
                        irc.send('PRIVMSG ' + channel + ' :GTV parameter missing: try !gtv help\n')
                        
                    elif data[4] == "upcoming":
                        cursor.execute("SELECT ID, TeamA, TeamB, Date, Time, League, Type, Stream, Shoutcaster FROM gtv_sc WHERE Public='yes' AND Done='no' ORDER BY Month DESC,Date DESC,Time DESC")
                        gtv = cursor.fetchall()
                        lengtv = len(gtv) -1
                        stop = 0
                        result = 0
                        while (stop < 1):
                            if lengtv >=0:
                                gtv1 = gtv[int(lengtv)]
                                msg = 'GTV matches: #' + gtv1[0] + ' ' + gtv1[1] + ' vs ' + gtv1[2] + ' @ ' + gtv1[3] + ' ' + gtv1[4] + " " + gtv1[5] + ' ' + gtv1[6]
                                if gtv1[7] != "":
                                    msg = msg + " !STREAMED!"
                                if gtv1[8] != "" and gtv1[7] == "":
                                    msg = msg + " !TS3CAST!"
                                irc.send('PRIVMSG ' + channel + ' :' + msg + '\n')
                                sleep(2)
                                result = 1
                            else:
                                stop = 1
                                if not result == 1:
                                    irc.send('PRIVMSG ' + channel + ' :No upcoming GTV match\n')
                            lengtv = lengtv - 1
                            
                    elif data[4] == "team":
                        if len(data) == 6:
                            if "\'" in text:
                                    text = text.replace("\'", "`")
                                    data = text.split()
                            cursor.execute("SELECT ID, TeamA, TeamB, Date, Time, League, Type FROM gtv_sc WHERE TeamA='" + data[5] + "' OR TeamB='" + data[5] + "' AND Done='yes' AND Public='yes' ORDER BY Month,Date,Time")
                            gtv = cursor.fetchall()
                            lengtv = len(gtv) -1
                            stop = 0
                            result = 0
                            while (stop < 1):
                                if lengtv >=0:
                                    gtv1 = gtv[int(lengtv)]
                                    irc.send('PRIVMSG ' + channel + ' :GTV #' + gtv1[0] + ': ' + gtv1[1] + ' vs ' + gtv1[2] + ' @ ' + gtv1[3] + ' ' + gtv1[4] + ' ' + gtv1[5] + ' ' + gtv1[6] + '\n')
                                    sleep(2)
                                    result = 1
                                else:
                                    stop = 1
                                lengtv = lengtv - 1
                            
                    elif data[4] == "bet":
                        if len(data) == 7:
                            if data[5].isdigit() == True:
                                cursor.execute("SELECT TeamA, TeamB FROM gtv_sc WHERE ID='" + data[5] + "' AND Spam='0' AND Public='yes'")
                                gtv = cursor.fetchall()
                                if not len(gtv) == 0:
                                    cursor.execute("SELECT TeamA, Draw, TeamB, Total FROM betting WHERE ID='" + data[5] + "'")
                                    bets = cursor.fetchone()
                                    if not bets == None:
                                        host = getnick[1]
                                        cursor.execute("SELECT * FROM betting_host WHERE ID='" + data[5] + "' AND host='" + host + "'")
                                        voting = cursor.fetchone()
                                        if voting == None:
                                            if data[6] == "1":
                                                cursor.execute("UPDATE betting SET TeamA='" + str(int(bets[0])+1) + "' WHERE ID='" + str(data[5]) + "'")
                                                cursor.execute("UPDATE betting SET Total='" + str(int(bets[3])+1) + "' WHERE ID='" + str(data[5]) + "'")
                                                cursor.execute("INSERT INTO `betting_host` (`ID`, `host` ) VALUES ('" + str(data[5]) + "', '" + host + "')")
                                                pc1=((int(bets[0])+1)*100)/(int(bets[3])+1)
                                                pc2=(int(bets[1])*100)/(int(bets[3])+1)
                                                pc3=(int(bets[2])*100)/(int(bets[3])+1)
                                                irc.send('PRIVMSG ' + channel + ' :Successfully betted: ' + gtv[0][0] + ' wins ' + str(pc1) + '% - Draw: ' + str(pc2) + '% - ' + gtv[0][1] + ' wins ' + str(pc3) + '% || Total bets: ' + str((int(bets[3])+1)) + '\n')
                                            elif data[6] == "2":
                                                cursor.execute("UPDATE betting SET Draw='" + str(int(bets[1])+1) + "' WHERE ID='" + str(data[5]) + "'")
                                                cursor.execute("UPDATE betting SET Total='" + str(int(bets[3])+1) + "' WHERE ID='" + str(data[5]) + "'")
                                                cursor.execute("INSERT INTO `betting_host` (`ID`, `host` ) VALUES ('" + str(data[5]) + "', '" + host + "')")
                                                pc1=(int(bets[0])*100)/(int(bets[3])+1)
                                                pc2=((int(bets[1])+1)*100)/(int(bets[3])+1)
                                                pc3=((int(bets[2]))*100)/(int(bets[3])+1)
                                                irc.send('PRIVMSG ' + channel + ' :Successfully betted: ' + gtv[0][0] + ' wins ' + str(pc1) + '% - Draw: ' + str(pc2) + '% - ' + gtv[0][1] + ' wins ' + str(pc3) + '% || Total bets: ' + str((int(bets[3])+1)) + '\n')
                                            elif data[6] == "3":
                                                cursor.execute("UPDATE betting SET TeamB='" + str(int(bets[2])+1) + "' WHERE ID='" + str(data[5]) + "'")
                                                cursor.execute("UPDATE betting SET Total='" + str(int(bets[3])+1) + "' WHERE ID='" + str(data[5]) + "'")
                                                cursor.execute("INSERT INTO `betting_host` (`ID`, `host` ) VALUES ('" + str(data[5]) + "', '" + host + "')")
                                                pc1=(int(bets[0])*100)/(int(bets[3])+1)
                                                pc2=(int(bets[1])*100)/(int(bets[3])+1)
                                                pc3=((int(bets[2])+1)*100)/(int(bets[3])+1)
                                                irc.send('PRIVMSG ' + channel + ' :Successfully betted: ' + gtv[0][0] + ' wins ' + str(pc1) + '% - Draw: ' + str(pc2) + '% - ' + gtv[0][1] + ' wins ' + str(pc3) + '% || Total bets: ' + str((int(bets[3])+1)) + '\n')
                                            else:
                                                irc.send('PRIVMSG ' + channel + ' :Wrong GTV command: !gtv bet <id> <1/2/3> || 1=TeamA wins | 2=Draw | 3=TeamB wins\n')
                                        else:
                                            irc.send('PRIVMSG ' + channel + ' :You have already betted on this match.\n')
                                else:
                                    irc.send('PRIVMSG ' + channel + ' :No GTV match found / bettings are closed\n')
                        else:
                            irc.send('PRIVMSG ' + channel + ' :Wrong GTV command: !gtv bet <id> <1/2/3> || 1=TeamA wins | 2=Draw | 3=TeamB wins\n')

                    elif data[4] == "demo":
                        if len(data) == 6:
                            if data[5].isdigit() == True:
                                cursor.execute("SELECT TeamA, TeamB, Demo FROM gtv_sc WHERE ID='" + data[5] + "'")
                                gtv = cursor.fetchall()
                                if not len(gtv) == 0:
                                    if gtv[0][2] == "":
                                        irc.send('PRIVMSG ' + channel + ' :No GTV demo available\n')
                                    else:
                                        irc.send('PRIVMSG ' + channel + ' :GTV demo of ' + gtv[0][0] + ' vs ' + gtv[0][1] + ': ' + gtv[0][2] + '\n')
                                else:
                                    irc.send('PRIVMSG ' + channel + ' :GTV ID wrong! !gtv demo <id>\n')
                        elif len(data) == 7:
                            if channel == "#urt-tv.admin":
                                cursor.execute("UPDATE gtv_sc SET Demo='" + str(data[6]) + "' WHERE ID='" + str(data[5]) + "'")
                                irc.send('PRIVMSG ' + channel + ' :GTV Demo added: #' + str(data[5]) + '\n')
                        else:
                            irc.send('PRIVMSG ' + channel + ' :GTV ID missing: !gtv demo <id>\n')

                    elif data[4] == "ip":
                        if len(data) == 6:
                            if data[5].isdigit() == True:
                                cursor.execute("SELECT TeamA, TeamB, Server, Stream, Shoutcaster FROM gtv_sc WHERE ID='" + data[5] + "'")
                                gtv = cursor.fetchall()
                                cursor.execute("SELECT status FROM status_new WHERE Name='ts3'")
                                ts3 = cursor.fetchone()
                                if not len(gtv) == 0:
                                    if gtv[0][2] == "":
                                        irc.send('PRIVMSG ' + channel + ' :No GTV ip available\n')
                                    else:
                                        msg = 'GTV IP ' + gtv[0][0] + ' vs ' + gtv[0][1] + ': ' + gtv[0][2]
                                        if gtv[0][3] != "":
                                            msg = msg + " | Stream: " + gtv[0][3]
                                        if gtv[0][4] != "" and gtv[0][3] == "":
                                            msg = msg + " | TS3Cast: " + ts3[0]
                                        irc.send('PRIVMSG ' + channel + ' :' + msg + '\n')
                                else:
                                    irc.send('PRIVMSG ' + channel + ' :GTV ID wrong! !gtv ip <id>\n')
                        elif len(data) == 7:
                            if channel == "#urt-tv.admin":
                                cursor.execute("UPDATE gtv_sc SET Server='" + str(data[6]) + "' WHERE ID='" + str(data[5]) + "'")
                                irc.send('PRIVMSG ' + channel + ' :GTV IP added: #' + str(data[5]) + '\n')
                        else:
                            irc.send('PRIVMSG ' + channel + ' :GTV ID missing: !gtv ip <id>\n')

                    elif data[4] == "help":
                        if len(data) == 5:
                            irc.send('NOTICE ' + nick + ' :Commands: !gtv <id>, !gtv upcoming, !gtv last, !gtv demo <id>, !gtv ip <id>, !gtv team <tag>\n')

                    elif data[4] == "last":
                        cursor.execute("SELECT ID, TeamA, TeamB, Date, Time, League, Type FROM gtv_sc WHERE Done='yes' AND Public='yes' ORDER BY Month DESC,date DESC,Time DESC")
                        gtv = cursor.fetchall()
                        if len(gtv) == 0:
                            irc.send('PRIVMSG ' + channel + ' :No GTV match found\n')
                        elif len(gtv) == 1:
                            gtv1 = gtv[0]
                            irc.send('PRIVMSG ' + channel + ' :GTV #' + gtv1[0] + ': ' + gtv1[1] + ' vs ' + gtv1[2] + ' @ ' + gtv1[3] + ' ' + gtv1[4] + ' ' + gtv1[5] + ' ' + gtv1[6] + '\n')
                            sleep(2)
                            irc.send('PRIVMSG ' + channel + ' :For more info: !gtv <id>\n')
                        elif len(gtv) == 2:
                            gtv1 = gtv[0]
                            irc.send('PRIVMSG ' + channel + ' :GTV #' + gtv1[0] + ': ' + gtv1[1] + ' vs ' + gtv1[2] + ' @ ' + gtv1[3] + ' ' + gtv1[4] + ' ' + gtv1[5] + ' ' + gtv1[6] + '\n')
                            sleep(2)
                            gtv1 = gtv[1]
                            irc.send('PRIVMSG ' + channel + ' :GTV #' + gtv1[0] + ': ' + gtv1[1] + ' vs ' + gtv1[2] + ' @ ' + gtv1[3] + ' ' + gtv1[4] + ' ' + gtv1[5] + ' ' + gtv1[6] + '\n')
                            sleep(2)
                            irc.send('PRIVMSG ' + channel + ' :For more info: !gtv <id>\n')
                        elif len(gtv) >= 3:
                            gtv1 = gtv[0]
                            irc.send('PRIVMSG ' + channel + ' :GTV #' + gtv1[0] + ': ' + gtv1[1] + ' vs ' + gtv1[2] + ' @ ' + gtv1[3] + ' ' + gtv1[4] + ' ' + gtv1[5] + ' ' + gtv1[6] + '\n')
                            sleep(2)
                            gtv1 = gtv[1]
                            irc.send('PRIVMSG ' + channel + ' :GTV #' + gtv1[0] + ': ' + gtv1[1] + ' vs ' + gtv1[2] + ' @ ' + gtv1[3] + ' ' + gtv1[4] + ' ' + gtv1[5] + ' ' + gtv1[6] + '\n')
                            sleep(2)
                            gtv1 = gtv[2]
                            irc.send('PRIVMSG ' + channel + ' :GTV #' + gtv1[0] + ': ' + gtv1[1] + ' vs ' + gtv1[2] + ' @ ' + gtv1[3] + ' ' + gtv1[4] + ' ' + gtv1[5] + ' ' + gtv1[6] + '\n')
                            sleep(2)
                            irc.send('PRIVMSG ' + channel + ' :For more info: !gtv <id>\n')

                    else:
                        if data[4].isdigit() == True:
                            cursor.execute("SELECT ID, League, Type, TeamA, TeamB, Date, Time, Score FROM gtv_sc WHERE ID='" + data[4] + "' AND Public='yes'")
                            gtv = cursor.fetchall()
                            if len(gtv) == 0:
                                irc.send('PRIVMSG ' + channel + ' :#' + str(data[4]) + ' not found\n')
                            else:
                                gtv1 = gtv[0]
                                cursor.execute("SELECT TeamA, Draw, TeamB, Total FROM betting WHERE ID='" + data[4] + "'")
                                bets = cursor.fetchone()
                                gtvbets = ""
                                gtvscore = ""
                                if not bets == None:
                                    if not bets[3] == "0":
                                        pc1=(int(bets[0])*100)/(int(bets[3]))
                                        pc2=(int(bets[1])*100)/(int(bets[3]))
                                        pc3=(int(bets[2])*100)/(int(bets[3]))
                                        gtvbets = " | Bets: " + str(gtv1[3]) + " wins " + str(pc1) + "% - Draw " + str(pc2) + "% - " + str(gtv1[4]) + " wins " + str(pc3) + "% || Total bets: " + str(bets[3])
                                if not gtv1[7] == "":
                                    gtvscore = " | Score: " + gtv1[7]
                                irc.send('PRIVMSG ' + channel + ' :GTV #' + gtv1[0] + ': ' + gtv1[1] + ' ' + gtv1[2] + ': ' + gtv1[3] + ' vs ' + gtv1[4] + ' ' + gtv1[5] + ' @ ' + gtv1[6] + '' + gtvscore + '' + gtvbets + '\n')
                                

                if data[2] == "#urt-tv.admin" or data[2] == "#urban-zone.radio":
                    if len(data) <= 4:
                        pass
                    
                    elif data[4] == "add":
                        if len(data) == 11:
                            cursor.execute("SELECT Status FROM status_new WHERE Name='ID'")
                            gtvid = cursor.fetchone()
                            gtvid = gtvid[0]
                            gtvid = int(gtvid) + 1
                            if "\'" in text:
                                text = text.replace("\'", "`")
                                data = text.split()
                            if "." in "." in data[7]:
                                gtvmonth = data[7].split(".")
                                gtvmonth = getall[4] + gtvmonth[1]
                            if ":" in data[8] and "." in data[7]:
                                cursor.execute("INSERT INTO `gtv_sc` (`ID`, `TeamA`, `TeamB`, `Date`, `Time`, `League`, `Type`, `Who`, `Server`, `Public`, `Done`, `Score`, `Demo`, `Month`, `Spam`, `Shoutcaster`, `Stream`, `Streamer`) VALUES ('" + str(gtvid) + "', '" + str(data[5]) + "', '" + str(data[6]) + "', '" + str(data[7]) + "', '" + str(data[8]) + "', '" + str(data[9]) + "', '" + str(data[10]) + "', '', '', 'no', 'no', '', '', '" + str(gtvmonth) + "', '0', '', '', '')")
                                cursor.execute("INSERT INTO `betting` (`ID`, `TeamA`, `TeamB`, `Draw`, `Total`) VALUES ('" + str(gtvid) + "', '0', '0', '0', '0')")
                                irc.send('PRIVMSG ' + channel + ' :GTV added: ID: #' + str(gtvid) + ' ' + str(data[5]) + ' vs ' + str(data[6]) + ' @ ' + str(data[7]) + ' ' + str(data[8]) + '\n')
                                cursor.execute("UPDATE status_new SET Status='" + str(gtvid) + "' WHERE Name='ID'")
                            else:
                                irc.send('PRIVMSG ' + channel + ' :YOU\'VE PUT THE FUCKING WRONG DATE OR TIME FORMAT\n')
                        else:
                            irc.send('PRIVMSG ' + channel + ' :GTV add parameter missing: !gtv add <TeamA> <TeamB> <date> <time> <league> <gametype>\n')

                    elif data[4] == "delete" and data[2] == "#urt-tv.admin":
                        cursor.execute("SELECT * FROM gtv_sc WHERE ID='" + data[5] + "'")
                        gtv1 = cursor.fetchone()
                        if not gtv1 == None:
                            if len(data) == 6:
                                cursor.execute("DELETE from gtv_sc WHERE id='" + str(data[5]) + "'")
                                irc.send('PRIVMSG ' + channel + ' :GTV deleted: #' + str(data[5]) + '\n')
                            else:
                                irc.send('PRIVMSG ' + channel + ' :GTV ID missing: !gtv delete <id>\n')
                        else:
                            irc.send('PRIVMSG ' + channel + ' :Wrong #' + str(data[5]) + '\n')

                    elif data[4] == "score":
                        if len(data) == 7:
                            cursor.execute("UPDATE gtv_sc SET Score='" + str(data[6]) + "' WHERE id='" + str(data[5]) + "'")
                            cursor.execute("UPDATE gtv_sc SET Done='yes' WHERE id='" + str(data[5]) + "'")
                            cursor.execute("UPDATE gtv_sc SET Spam='2' WHERE ID='" + str(data[5]) + "'")
                            irc.send('PRIVMSG ' + channel + ' :GTV score added: #' + str(data[5]) + '\n')
                        else:
                            irc.send('PRIVMSG ' + channel + ' :GTV ID or Score missing: !gtv score <id> <x-x>\n')

                    elif data[4] == "done":
                        if len(data) == 8:
                            cursor.execute("SELECT * FROM gtv_sc WHERE ID='" + data[5] + "'")
                            gtv1 = cursor.fetchone()
                            if not gtv1 == None:
                                cursor.execute("UPDATE gtv_sc SET Score='" + str(data[6]) + "' WHERE id='" + str(data[5]) + "'")
                                cursor.execute("UPDATE gtv_sc SET Done='yes' WHERE id='" + str(data[5]) + "'")
                                cursor.execute("UPDATE gtv_sc SET Spam='2' WHERE ID='" + str(data[5]) + "'")
                                cursor.execute("UPDATE gtv_sc SET Demo='" + str(data[7]) + "' WHERE ID='" + str(data[5]) + "'")
                                irc.send('PRIVMSG ' + channel + ' :GTV done added: #' + str(data[5]) + '\n')
                            else:
                                irc.send('PRIVMSG ' + channel + ' :Wrong ID: #' + str(data[5]) + '\n')
                        else:
                            irc.send('PRIVMSG ' + channel + ' :GTV ID or Score missing: !gtv done <id> <x-x> <demo>\n')

                    elif data[4] == "topic" and data[2] == "#urt-tv.admin":
                        if len(data) >= 6:
                                if data [5] == "default":
                                    irc.send('TOPIC #urt-tv :9,1 UrT-TV 0>>> 4http://www.urt-tv.info/0 | 8!gtv upcoming0 | 8!gtv last 0| 7Announced times are CET (Paris, Berlin, Amsterdam..) 0|10 Please behave, and speak english ! \n')
                                    irc.send('PRIVMSG ' + channel + ' :Topic changed\n')
                                else:
                                    stop = 0
                                    num = 5
                                    what = ""
                                    lenge = len(data)
                                    while(stop < 1):
                                        what = what  + " " + data[int(num)]
                                        num = int(num) + 1
                                        if int(num) == int(lenge):
                                            stop = 1
                                    irc.send('TOPIC #urt-tv :' + str(what) + '\n')
                                    irc.send('PRIVMSG ' + channel + ' :Topic changed\n')
                        else:
                            irc.send('PRIVMSG ' + channel + ' :GTV text missing: !gtv topic <text>\n')

                    elif data[4] == "adv" and data[2] == "#urt-tv.admin":
                        if len(data) >= 6:
                                stop = 0
                                num = 5
                                what = ""
                                lenge = len(data)
                                while(stop < 1):
                                    what = what  + " " + data[int(num)]
                                    num = int(num) + 1
                                    if int(num) == int(lenge):
                                        stop = 1
                                irc.send('PRIVMSG #urt-tv :!msg ' + str(what) + '\n')
                                irc.send('PRIVMSG ' + channel + ' :MSG spammed\n')
                        else:
                            irc.send('PRIVMSG ' + channel + ' :GTV text missing: !gtv adv <text>\n')

                    elif data[4] == "say" and data[2] == "#urt-tv.admin":
                        if len(data) >= 6:
                            ident_user = getnick[1].split("@")
                            ident_user = ident_user[0]
                            if ident_user in admins:
                                stop = 0
                                num = 5
                                what = ""
                                lenge = len(data)
                                while(stop < 1):
                                    what = what  + " " + data[int(num)]
                                    num = int(num) + 1
                                    if int(num) == int(lenge):
                                        stop = 1
                                irc.send('PRIVMSG #urt-tv :' + str(what) + '\n')
                                irc.send('PRIVMSG ' + channel + ' :I said that in pub chan.\n')
                            else:
                                irc.send('PRIVMSG ' + channel + ' :You dont have the access to use this.\n')
                        else:
                            irc.send('PRIVMSG ' + channel + ' :GTV text missing: !gtv adv <text>\n')

                    elif data[4] == "autospam" and data[2] == "#urt-tv.admin":
                        if len(data) == 7:
                            if data[6] == "on":
                                cursor.execute("UPDATE gtv_sc SET Spam='0' WHERE id='" + str(data[5]) + "'")
                                irc.send('PRIVMSG ' + channel + ' :GTV autospam enabled: #' + str(data[5]) + '\n')
                            elif data[6] == "off":
                                cursor.execute("UPDATE gtv_sc SET Spam='2' WHERE id='" + str(data[5]) + "'")
                                irc.send('PRIVMSG ' + channel + ' :GTV autospam disabled: #' + str(data[5]) + '\n')
                        else:
                            irc.send('PRIVMSG ' + channel + ' :GTV ID or option missing: !gtv autospam <id> <on/off>\n')

                    elif data[4] == "spam" and data[2] == "#urt-tv.admin":
                        cursor.execute("SELECT status FROM status_new WHERE Name='ts3'")
                        ts3 = cursor.fetchone()
                        if len(data) == 6:
                            if data[5].isdigit() == True:
                                cursor.execute("SELECT TeamA, TeamB, Server, Stream, Shoutcaster FROM gtv_sc WHERE ID='" + data[5] + "'")
                                gtv1 = cursor.fetchone()
                                if not gtv1 == None:
                                    if gtv1[3] != "":
                                        msg = " - Stream: " + gtv1[3]
                                    elif gtv1[3] == "" and gtv1[4] != "":
                                        msg = " - TS3CAST: " + ts3[0]
                                    else:
                                        msg = ""
                                    irc.send('PRIVMSG #urt-tv :!gtvmsg Watch Now! ' + gtv1[0] + ' vs ' + gtv1[1] + ' - /connect ' + gtv1[2] + msg + '\n')
                                    irc.send('PRIVMSG #urt-tv :!msg [GTV] Watch Now! ' + gtv1[0] + ' vs ' + gtv1[1] + ' - /connect ' + gtv1[2] + msg + '\n')
                                    cursor.execute("UPDATE gtv_sc SET Spam='2' WHERE ID='" + str(gtv1[0]) + "'")
                                    irc.send('PRIVMSG ' + channel + ' :GTV spammed\n')
                                else:
                                    irc.send('PRIVMSG ' + channel + ' :Wrong ID: #' + str(data[5]) + '\n')
                        elif len(data) == 7:
                            if data[5].isdigit() == True and data[6].isdigit() == True:
                                cursor.execute("SELECT TeamA, TeamB, Server, Stream, Shoutcaster FROM gtv_sc WHERE ID='" + data[5] + "'")
                                gtv1 = cursor.fetchone()
                                cursor.execute("SELECT TeamA, TeamB, Server, Stream, Shoutcaster FROM gtv_sc WHERE ID='" + data[6] + "'")
                                gtv2 = cursor.fetchone()
                                if not gtv1 == None and not gtv2 == None:
                                    if gtv1[3] != "":
                                        msg1 = " - Stream: " + gtv1[3]
                                    elif gtv1[3] == "" and gtv1[4] != "":
                                        msg = " - TS3CAST: " + ts3[0]
                                    else:
                                        msg1 = ""
                                    if gtv2[3] != "":
                                        msg2 = " - Stream: " + gtv1[3]
                                    elif gtv1[3] == "" and gtv1[4] != "":
                                        msg = " - TS3CAST: " + ts3[0]
                                    else:
                                        msg2 = ""
                                    irc.send('PRIVMSG #urt-tv :!gtvmsg Watch Now! ' + gtv1[0] + ' vs ' + gtv1[1] + ' - /connect ' + gtv1[2] + msg1 + ' | ' + gtv2[0] + ' vs ' + gtv2[1] + ' - /connect ' + gtv2[2] + msg2 + '\n')
                                    irc.send('PRIVMSG #urt-tv :!msg [GTV] Watch Now! ' + gtv1[0] + ' vs ' + gtv1[1] + ' - /connect ' + gtv1[2] + msg1 + ' | ' + gtv2[0] + ' vs ' + gtv2[1] + ' - /connect ' + gtv2[2] + msg2 + '\n')
                                    cursor.execute("UPDATE gtv_sc SET Spam='2' WHERE ID='" + str(gtv1[0]) + "'")
                                    cursor.execute("UPDATE gtv_sc SET Spam='2' WHERE ID='" + str(gtv2[0]) + "'")
                                    irc.send('PRIVMSG ' + channel + ' :GTV spammed\n')
                                else:
                                    irc.send('PRIVMSG ' + channel + ' :Wrong ID: #' + str(data[5]) + ' or #' + str(data[6]) + '\n')
                        elif len(data) == 8:
                            if data[5].isdigit() == True and data[5].isdigit() == True and data[6].isdigit() == True and data[7].isdigit() == True:
                                cursor.execute("SELECT TeamA, TeamB, Server, Stream, Shoutcaster FROM gtv_sc WHERE ID='" + data[5] + "'")
                                gtv1 = cursor.fetchone()
                                cursor.execute("SELECT TeamA, TeamB, Server, Stream, Shoutcaster FROM gtv_sc WHERE ID='" + data[6] + "'")
                                gtv2 = cursor.fetchone()
                                cursor.execute("SELECT TeamA, TeamB, Server, Stream, Shoutcaster FROM gtv_sc WHERE ID='" + data[7] + "'")
                                gtv3 = cursor.fetchone()
                                if not gtv1 == None and not gtv2 == None and not gtv3 == None:
                                    if gtv1[3] != "":
                                        msg1 = " - Stream: " + gtv1[3]
                                    elif gtv1[3] == "" and gtv1[4] != "":
                                        msg = " - TS3CAST: " + ts3[0]
                                    else:
                                        msg1 = ""
                                    if gtv2[3] != "":
                                        msg2 = " - Stream: " + gtv1[3]
                                    elif gtv1[3] == "" and gtv1[4] != "":
                                        msg = " - TS3CAST: " + ts3[0]
                                    else:
                                        msg2 = ""
                                    if gtv3[3] != "":
                                        msg3 = " - Stream: " + gtv1[3]
                                    elif gtv1[3] == "" and gtv1[4] != "":
                                        msg = " - TS3CAST: " + ts3[0]
                                    else:
                                        msg3 = ""
                                    irc.send('PRIVMSG #urt-tv :!gtvmsg Watch Now! ' + gtv1[0] + ' vs ' + gtv1[1] + ' - /connect ' + gtv1[2] + msg1 + ' | ' + gtv2[0] + ' vs ' + gtv2[1] + ' - /connect ' + gtv2[2] + msg2 + ' | ' + gtv3[0] + ' vs ' + gtv3[1] + ' - /connect ' + gtv3[2] + msg3 + '\n')
                                    irc.send('PRIVMSG #urt-tv :!msg [GTV] Watch Now! ' + gtv1[0] + ' vs ' + gtv1[1] + ' - /connect ' + gtv1[2] + msg1 + ' | ' + gtv2[0] + ' vs ' + gtv2[1] + ' - /connect ' + gtv2[2] + msg2 + ' | ' + gtv3[0] + ' vs ' + gtv3[1] + ' - /connect ' + gtv3[2] + msg3 + '\n')
                                    cursor.execute("UPDATE gtv_sc SET Spam='2' WHERE ID='" + str(gtv1[0]) + "'")
                                    cursor.execute("UPDATE gtv_sc SET Spam='2' WHERE ID='" + str(gtv2[0]) + "'")
                                    cursor.execute("UPDATE gtv_sc SET Spam='2' WHERE ID='" + str(gtv3[0]) + "'")
                                    irc.send('PRIVMSG ' + channel + ' :GTV spammed\n')
                                else:
                                    irc.send('PRIVMSG ' + channel + ' :Wrong ID: #' + str(data[5]) + ' or #' + str(data[6]) + ' or #' + str(data[7]) + '\n')
                        else:
                            irc.send('PRIVMSG ' + channel + ' :GTV ID missing: !gtv spam <id> <id> <id>\n')

                    elif data[4] == "type":
                        if len(data) >= 7:
                            cursor.execute("SELECT * FROM gtv_sc WHERE ID='" + data[5] + "'")
                            gtv1 = cursor.fetchone()
                            if not gtv1 == None:
                                cursor.execute("UPDATE gtv_sc SET Type='" + str(data[6]) + "' WHERE id='" + str(data[5]) + "'")
                                irc.send('PRIVMSG ' + channel + ' :GTV type changed: #' + str(data[5]) + '\n')
                            else:
                                irc.send('PRIVMSG ' + channel + ' :Wrong ID: #' + str(data[5]) + '\n')
                        else:
                            irc.send('PRIVMSG ' + channel + ' :Cmd, GTV ID or new value missing: !gtv type <id> <new value>\n')

                    elif data[4] == "time":
                        if len(data) >= 7:
                            cursor.execute("SELECT * FROM gtv_sc WHERE ID='" + data[5] + "'")
                            gtv1 = cursor.fetchone()
                            if not gtv1 == None:
                                if ":" in data[6]:
                                    cursor.execute("UPDATE gtv_sc SET Time='" + str(data[6]) + "' WHERE id='" + str(data[5]) + "'")
                                    irc.send('PRIVMSG ' + channel + ' :GTV time changed: #' + str(data[5]) + '\n')
                                else:
                                    irc.send('PRIVMSG ' + channel + ' :YOU\'VE PUT THE FUCKING WRONG TIME FORMAT\n')
                            else:
                                irc.send('PRIVMSG ' + channel + ' :Wrong ID: #' + str(data[5]) + '\n')
                        else:
                            irc.send('PRIVMSG ' + channel + ' :Cmd, GTV ID or new value missing: !gtv time <id> <new value>\n')

                    elif data[4] == "date":
                        if len(data) >= 7:
                            cursor.execute("SELECT * FROM gtv_sc WHERE ID='" + data[5] + "'")
                            gtv1 = cursor.fetchone()
                            if not gtv1 == None:
                                if "." in data[6]:
                                    month = data[6].split(".")
                                    month = month[2] + month[1]
                                    cursor.execute("UPDATE gtv_sc SET Date='" + str(data[6]) + "' WHERE id='" + str(data[5]) + "'")
                                    cursor.execute("UPDATE gtv_sc SET Month='" + str(month) + "' WHERE id='" + str(data[5]) + "'")
                                    irc.send('PRIVMSG ' + channel + ' :GTV date changed: #' + str(data[5]) + '\n')
                                else:
                                    irc.send('PRIVMSG ' + channel + ' :YOU\'VE PUT THE FUCKING WRONG DATE FORMAT\n')
                            else:
                                irc.send('PRIVMSG ' + channel + ' :Wrong ID: #' + str(data[5]) + '\n')
                        else:
                            irc.send('PRIVMSG ' + channel + ' :Cmd, GTV ID or new value missing: !gtv date <id> <new value>\n')

                    elif data[4] == "league":
                        if len(data) >= 7:
                            cursor.execute("SELECT * FROM gtv_sc WHERE ID='" + data[5] + "'")
                            gtv1 = cursor.fetchone()
                            if not gtv1 == None:
                                cursor.execute("UPDATE gtv_sc SET League='" + str(data[6]) + "' WHERE id='" + str(data[5]) + "'")
                                irc.send('PRIVMSG ' + channel + ' :GTV league changed: #' + str(data[5]) + '\n')
                            else:
                                irc.send('PRIVMSG ' + channel + ' :Wrong ID: #' + str(data[5]) + '\n')
                        else:
                            irc.send('PRIVMSG ' + channel + ' :Cmd, GTV ID or new value missing: !gtv league <id> <new value>\n')

                    elif data[4] == "team1":
                        if len(data) >= 7:
                            cursor.execute("SELECT * FROM gtv_sc WHERE ID='" + data[5] + "'")
                            gtv1 = cursor.fetchone()
                            if not gtv1 == None:
                                cursor.execute("UPDATE gtv_sc SET TeamA='" + str(data[6]) + "' WHERE id='" + str(data[5]) + "'")
                                irc.send('PRIVMSG ' + channel + ' :GTV TeamA changed: #' + str(data[5]) + '\n')
                            else:
                                irc.send('PRIVMSG ' + channel + ' :Wrong ID: #' + str(data[5]) + '\n')
                        else:
                            irc.send('PRIVMSG ' + channel + ' :Cmd, GTV ID or new value missing: !gtv team1 <id> <new value>\n')

                    elif data[4] == "team2":
                        if len(data) >= 7:
                            cursor.execute("SELECT * FROM gtv_sc WHERE ID='" + data[5] + "'")
                            gtv1 = cursor.fetchone()
                            if not gtv1 == None:
                                cursor.execute("UPDATE gtv_sc SET TeamB='" + str(data[6]) + "' WHERE id='" + str(data[5]) + "'")
                                irc.send('PRIVMSG ' + channel + ' :GTV TeamB changed: #' + str(data[5]) + '\n')
                            else:
                                irc.send('PRIVMSG ' + channel + ' :Wrong ID: #' + str(data[5]) + '\n')
                        else:
                            irc.send('PRIVMSG ' + channel + ' :Cmd, GTV ID or new value missing: !gtv team2 <id> <new value>\n')

                    elif data[4] == "servers":
                        if data[2] == "#urban-zone.radio":
                            cursor.execute("SELECT ID,IP,Admin,Camera FROM servers where id='3' or id='4'")
                            gtv1 = cursor.fetchall()
                        else:
                            cursor.execute("SELECT ID,IP,Admin,Camera FROM servers")
                            gtv1 = cursor.fetchall()
                        if not len(gtv1) == 0:
                            count = 0
                            while len(gtv1) > count:
                                irc.send('PRIVMSG ' + channel + ' :GTV #' + str(gtv1[count][0]) + ' IP: ' + str(gtv1[count][1]) + ' - Admin: ' + str(gtv1[count][2]) + ' - Camera: ' + str(gtv1[count][3]) + '\n')
                                sleep(2)
                                count = count + 1
                        else:
                            irc.send('PRIVMSG ' + channel + ' :No servers set.\n')


                    elif data[4] == "list":
                        cursor.execute("SELECT * FROM gtv_sc WHERE Done='no' AND Public='yes' ORDER BY Month DESC,date DESC,Time DESC")
                        gtv = cursor.fetchall()
                        lengtv = len(gtv) -1
                        stop = 0
                        result = 0
                        while (stop < 1):
                            if lengtv >=0:
                                gtv1 = gtv[int(lengtv)]
                                irc.send('PRIVMSG ' + channel + ' :#' + gtv1[0] + ' ' + gtv1[1] + ' vs ' + gtv1[2] + ' - ' + gtv1[3] + ' - ' + gtv1[4] + ' - ' + gtv1[5] + ' ' + gtv1[6] + ' - `' + gtv1[7] + '` - ' + gtv1[8] + '\n')
                                sleep(2)
                                result = 1
                            else:
                                stop = 1
                                if not result == 1:
                                    irc.send('PRIVMSG ' + channel + ' :No taken GTV match\n')
                            lengtv = lengtv - 1

                    elif data[4] == "free":
                        cursor.execute("SELECT * FROM gtv_sc WHERE Done='no' AND Public='no' ORDER BY Month DESC,date DESC,Time DESC")
                        gtv = cursor.fetchall()
                        lengtv = len(gtv) -1
                        stop = 0
                        result = 0
                        while (stop < 1):
                            if lengtv >=0:
                                gtv1 = gtv[int(lengtv)]
                                irc.send('PRIVMSG ' + channel + ' :#' + gtv1[0] + ' ' + gtv1[1] + ' vs ' + gtv1[2] + ' - ' + gtv1[3] + ' @ ' + gtv1[4] + ' - ' + gtv1[5] + ' ' + gtv1[6] + '\n')
                                sleep(2)
                                result = 1
                            else:
                                stop = 1
                                if not result == 1:
                                    irc.send('PRIVMSG ' + channel + ' :No free GTV match\n')
                            lengtv = lengtv - 1

                    elif data[4] == "take":
                        if len(data) == 6:
                            cursor.execute("SELECT * FROM gtv_sc WHERE ID='" + data[5] + "'")
                            gtv1 = cursor.fetchone()
                            if not gtv1 == None:
                                cursor.execute("UPDATE gtv_sc SET Who='" + str(nick) + "' WHERE id='" + str(data[5]) + "'")
                                cursor.execute("UPDATE gtv_sc SET Public='yes' WHERE id='" + str(data[5]) + "'")
                                irc.send('PRIVMSG ' + channel + ' :GTV match taken: #' + str(data[5]) + '\n')
                            else:
                                irc.send('PRIVMSG ' + channel + ' :Wrong ID: #' + str(data[5]) + '\n')
                        elif len(data) == 7:
                            cursor.execute("SELECT * FROM gtv_sc WHERE ID='" + data[5] + "'")
                            gtv1 = cursor.fetchone()
                            if not gtv1 == None:
                                cursor.execute("UPDATE gtv_sc SET Who='" + str(nick) + "' WHERE id='" + str(data[5]) + "'")
                                cursor.execute("UPDATE gtv_sc SET Public='yes' WHERE id='" + str(data[5]) + "'")
                                cursor.execute("UPDATE gtv_sc SET Server='" + str(data[6]) + "' WHERE id='" + str(data[5]) + "'")
                                irc.send('PRIVMSG ' + channel + ' :GTV match taken: #' + str(data[5]) + '\n')
                            else:
                                irc.send('PRIVMSG ' + channel + ' :Wrong ID: #' + str(data[5]) + '\n')
                        else:
                            irc.send('PRIVMSG ' + channel + ' :GTV ID missing: !gtv take <id> </ip/>\n')

                    elif data[4] == "force":
                        if len(data) == 7:
                            cursor.execute("SELECT * FROM gtv_sc WHERE ID='" + data[5] + "'")
                            gtv1 = cursor.fetchone()
                            if not gtv1 == None:
                                cursor.execute("UPDATE gtv_sc SET Who='" + str(data[6]) + "' WHERE id='" + str(data[5]) + "'")
                                cursor.execute("UPDATE gtv_sc SET Public='yes' WHERE id='" + str(data[5]) + "'")
                                irc.send('PRIVMSG ' + channel + ' :GTV match taken (forced): #' + str(data[5]) + '\n')
                            else:
                                irc.send('PRIVMSG ' + channel + ' :Wrong ID: #' + str(data[5]) + '\n')
                        elif len(data) == 8:
                            cursor.execute("SELECT * FROM gtv_sc WHERE ID='" + data[5] + "'")
                            gtv1 = cursor.fetchone()
                            if not gtv1 == None:
                                cursor.execute("UPDATE gtv_sc SET Who='" + str(data[6]) + "' WHERE id='" + str(data[5]) + "'")
                                cursor.execute("UPDATE gtv_sc SET Public='yes' WHERE id='" + str(data[5]) + "'")
                                cursor.execute("UPDATE gtv_sc SET Server='" + str(data[7]) + "' WHERE id='" + str(data[5]) + "'")
                                irc.send('PRIVMSG ' + channel + ' :GTV match taken (forced): #' + str(data[5]) + '\n')
                            else:
                                irc.send('PRIVMSG ' + channel + ' :Wrong ID: #' + str(data[5]) + '\n')
                        else:
                            irc.send('PRIVMSG ' + channel + ' :GTV ID missing: !gtv force <id> <nick> <ip>\n')

                    elif data[4] == "remove":
                        if len(data) == 6:
                            cursor.execute("SELECT * FROM gtv_sc WHERE ID='" + data[5] + "'")
                            gtv1 = cursor.fetchone()
                            if not gtv1 == None:
                                cursor.execute("UPDATE gtv_sc SET Who='' WHERE id='" + str(data[5]) + "'")
                                cursor.execute("UPDATE gtv_sc SET Public='no' WHERE id='" + str(data[5]) + "'")
                                cursor.execute("UPDATE gtv_sc SET Server='' WHERE id='" + str(data[5]) + "'")
                                irc.send('PRIVMSG ' + channel + ' :GTV match removed: #' + str(data[5]) + '\n')
                            else:
                                irc.send('PRIVMSG ' + channel + ' :Wrong ID: #' + str(data[5]) + '\n')
                        else:
                            irc.send('PRIVMSG ' + channel + ' :GTV ID missing: !gtv remove <id> <ip>\n')

            if data[3] == ":!sc":
                channel = data[2]
                if data[2] == "#urban-zone.radio" or data[2] == "#urt-tv.admin":
                    if len(data) <= 4:
                        pass

                    elif data[4] == "list":
                        cursor.execute("SELECT ID, TeamA, TeamB, Date, Time, League, Type, Shoutcaster, Streamer, Stream FROM gtv_sc WHERE Done='no' AND NOT Shoutcaster='' ORDER BY Month DESC,date DESC,Time DESC")
                        gtv = cursor.fetchall()
                        lengtv = len(gtv) -1
                        stop = 0
                        result = 0
                        while (stop < 1):
                            if lengtv >=0:
                                gtv1 = gtv[int(lengtv)]
                                if gtv1[7] != "" and gtv1[8] == "":
                                    irc.send('PRIVMSG ' + channel + ' :#' + gtv1[0] + ' ' + gtv1[1] + ' vs ' + gtv1[2] + ' - ' + gtv1[3] + ' - ' + gtv1[4] + ' - ' + gtv1[5] + ' ' + gtv1[6] + ' - TS3CAST: `' + gtv1[7] + '`\n')
                                else:
                                    irc.send('PRIVMSG ' + channel + ' :#' + gtv1[0] + ' ' + gtv1[1] + ' vs ' + gtv1[2] + ' - ' + gtv1[3] + ' - ' + gtv1[4] + ' - ' + gtv1[5] + ' ' + gtv1[6] + ' - Shoutcast: `' + gtv1[7] + '` - Streamer: ' + gtv1[8] + ' - Stream: ' + gtv1[9] + '\n')
                                sleep(2)
                                result = 1
                            else:
                                stop = 1
                                if not result == 1:
                                    irc.send('PRIVMSG ' + channel + ' :No taken GTV match\n')
                            lengtv = lengtv - 1

                    elif data[4] == "stream":
                        if len(data) == 7:
                            cursor.execute("SELECT * FROM gtv_sc WHERE ID='" + data[5] + "'")
                            gtv1 = cursor.fetchone()
                            if not gtv1 == None:
                                cursor.execute("UPDATE gtv_sc SET Stream='" + str(data[6]) + "' WHERE id='" + str(data[5]) + "'")
                                irc.send('PRIVMSG ' + channel + ' :Stream changed: #' + str(data[5]) + '\n')
                            else:
                                irc.send('PRIVMSG ' + channel + ' :Wrong ID: #' + str(data[5]) + '\n')
                        else:
                            irc.send('PRIVMSG ' + channel + ' :[ERROR] !sc stream <id> <link>\n')
                            lengtv = lengtv - 1

                    elif data[4] == "streamer":
                        if len(data) == 7:
                            cursor.execute("SELECT * FROM gtv_sc WHERE ID='" + data[5] + "'")
                            gtv1 = cursor.fetchone()
                            if not gtv1 == None:
                                cursor.execute("UPDATE gtv_sc SET Streamer='" + str(data[6]) + "' WHERE id='" + str(data[5]) + "'")
                                irc.send('PRIVMSG ' + channel + ' :Streamer changed: #' + str(data[5]) + '\n')
                            else:
                                irc.send('PRIVMSG ' + channel + ' :Wrong ID: #' + str(data[5]) + '\n')
                        else:
                            irc.send('PRIVMSG ' + channel + ' :[ERROR] !sc streamer <id> <streamer>\n')
                            lengtv = lengtv - 1

                    elif data[4] == "shoutcaster":
                        if len(data) == 7:
                            cursor.execute("SELECT * FROM gtv_sc WHERE ID='" + data[5] + "'")
                            gtv1 = cursor.fetchone()
                            if not gtv1 == None:
                                cursor.execute("UPDATE gtv_sc SET Shoutcaster='" + str(data[6]) + "' WHERE id='" + str(data[5]) + "'")
                                irc.send('PRIVMSG ' + channel + ' :Shoutcaster changed: #' + str(data[5]) + '\n')
                            else:
                                irc.send('PRIVMSG ' + channel + ' :Wrong ID: #' + str(data[5]) + '\n')
                        else:
                            irc.send('PRIVMSG ' + channel + ' :[ERROR] !sc shoutcaster <id> <shoutcaster>\n')

                    elif data[4] == "take":
                        if len(data) == 9:
                            cursor.execute("SELECT * FROM gtv_sc WHERE ID='" + data[5] + "' AND NOT Who=''")
                            gtv1 = cursor.fetchone()
                            if not gtv1 == None:
                                cursor.execute("UPDATE gtv_sc SET Shoutcaster='" + str(data[6]) + "' WHERE id='" + str(data[5]) + "'")
                                cursor.execute("UPDATE gtv_sc SET Streamer='" + str(data[7]) + "' WHERE id='" + str(data[5]) + "'")
                                cursor.execute("UPDATE gtv_sc SET Stream='" + str(data[8]) + "' WHERE id='" + str(data[5]) + "'")
                                irc.send('PRIVMSG ' + channel + ' :Shoutcast match taken: #' + str(data[5]) + '\n')
                            else:
                                irc.send('PRIVMSG ' + channel + ' :Wrong ID or no GTV man signed up yet: #' + str(data[5]) + '\n')
                            
                        elif len(data) == 7:# and data[2] == "#urt-tv.admin":
                            cursor.execute("SELECT * FROM gtv_sc WHERE ID='" + data[5] + "' AND NOT Who=''")
                            gtv1 = cursor.fetchone()
                            if not gtv1 == None:
                                cursor.execute("UPDATE gtv_sc SET Shoutcaster='" + str(data[6]) + "' WHERE id='" + str(data[5]) + "'")
                                irc.send('PRIVMSG ' + channel + ' :TS3-Shoutcast match taken: #' + str(data[5]) + '\n')
                            else:
                                irc.send('PRIVMSG ' + channel + ' :Wrong ID or no GTV man signed up yet: #' + str(data[5]) + '\n')
                        else:
                            irc.send('PRIVMSG ' + channel + ' :[ERROR] !sc take <id> <shoutcaster> <steamer> <link>\n')

                    elif data[4] == "remove":
                        if len(data) == 6:
                            cursor.execute("SELECT * FROM gtv_sc WHERE ID='" + data[5] + "'")
                            gtv1 = cursor.fetchone()
                            if not gtv1 == None:
                                cursor.execute("UPDATE gtv_sc SET Shoutcaster='' WHERE id='" + str(data[5]) + "'")
                                cursor.execute("UPDATE gtv_sc SET Streamer='' WHERE id='" + str(data[5]) + "'")
                                cursor.execute("UPDATE gtv_sc SET Stream='' WHERE id='" + str(data[5]) + "'")
                                irc.send('PRIVMSG ' + channel + ' :Shoutcast match removed: #' + str(data[5]) + '\n')
                            else:
                                irc.send('PRIVMSG ' + channel + ' :Wrong ID: #' + str(data[5]) + '\n')
                        else:
                            irc.send('PRIVMSG ' + channel + ' :[ERROR] !sc remove <id>\n')

    except socket.error:
        reconnect()
        continue
