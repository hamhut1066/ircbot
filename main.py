#!/usr/bin/env python 
#[':hamhut1066!~hamhut@vortis.xen.tardis.ed.ac.uk', 'PRIVMSG', '#test_2', ':the', 'string']
#[0]- the domain and user, [1] - the type of message being sent, [2] - the channel-name, [3..] the input string from the user
 
import sys 
import socket 
import string 
import sqlite3

HOST="irc.imaginarynet.org.uk" 
PORT=6667 
NICK="hbot" 
IDENT="hbot" 
REALNAME="hbot" 
CHAN="#compsoc" 
readbuffer="" 
conn = sqlite3.connect("ircbot.db") 

#--------------------------------------database-----------------------------
def database():
	cursor = conn.cursor()
	return cursor

def update(query):
	database().execute(query.lower())
	conn.commit()


def queryone(query):
	cursor = database()
	cursor.execute(query.lower())

	return cursor.fetchone()

def queryall(query):
	cursor = database()
	cursor.execute(query.lower())

	all_rows = cursor.fetchall()
	#return "queryall"
	return all_rows
#----------------------------------end-database-----------------------------

def parsebot(user, userin):
	#this is where all the heavy lifting is!
	inlist = userin.split(' ')
	q = inlist[0]
	command = q.split('.')[1]
	tail = ' '.join(inlist[1:])
	if userin.startswith('..'):
		updatebot(user, userin)
		return None
	elif command == "":
		return None
	elif command == "myswears":
		ret = queryone("Select * from sw_count where name = '%s'" % user)
		if ret == None:
			return None
		return "%s: %s swears" % (ret[0], ret[1])
	elif command == "swears":
		ret = queryone("Select * from sw_count where name = '%s'" % tail)
		if ret == None:
			return None
		return "%s: %s swears" % (ret[0], ret[1])
	elif command == "hello":
		return "hello %s" % user
	elif command == "slap":
		return "%s slaps %s" % (user, tail)
	elif command == "addsw":
		#adds a swear word to the list
		#first check if word exists
		if queryone("select * from swords where name = '%s'" % tail) == None and len(tail) > 2:
			try:
				args = tail.split(' ')
				return adminupdate(user, "INSERT INTO swords values('%s', %s)" % (args[0],args[1] ))
			except:
				return ".addsw <name> <weight>"
		else:
			return "%s already exists" % tail
	elif command == "lsw":
		#lists swear words
		tmp = queryall("select name from swords")
		ret = ""
		for i in tmp:
			ret += "%s, " % i[0]
		return ret
	elif command == "reset":
		adminupdate(user, "update sw_count set swear_count = 0 where name = '%s'" % tail)
	elif command == "op":
		#give someone admin rights
		if queryone("select * from admin where name = '%s'" % tail) == None:
			return adminupdate (user, "insert into admin values('%s')" % tail, "%s is now op" % tail)
		else:
			return "user is already op"
	elif command == "nop":
		#give someone admin rights
		if queryone("select * from admin where name = '%s'" % tail) != None:
			return adminupdate (user, "delete from admin where name = '%s'" % tail, "%s is no longer op" % tail)
		else:
			return None
	elif command == "lop":
		tmp = queryall("select * from admin")
		ret = ""
		for i in tmp:
			ret += "%s, " % i
		return ret
	elif command == "leaderboard":
		tmp = queryall("select * from sw_count order by swear_count desc limit 5")
		ret = ""
		for i in tmp:
			ret += "%s: %s, " % (i[0], i[1])
		return ret
		
		
	else:
		return "%s %ss %s" % (user, command, tail)

def adminupdate(user, query, msg=None):
	if queryone("select name from admin where name = '%s'" % user) == None:
		#no permission
		return "permission denied..."
	else:
		update(query)
		return msg
def updatebot(user, userin):
	#this doesn't return anything, but does things like update the swear count
	#add user to the database if needed
	try:
		out = queryone("Select * from sw_count where name = '%s'" % user)
		if out == None and '.' not in user and "bot" not in user:
			update("INSERT INTO sw_count values('%s', 0)" % user)
	except:
		update("INSERT INTO sw_count values('%s', 0)" % user)

	#this needs to check if a user uses a swear word
	#read swear words from the database
	sweardb = queryall("Select name from swords")
	for i in sweardb:
		if i[0] in userin:
			#add a swear to the database
			count = queryone("select count from swords where name = '%s'" % i[0])
			update("UPDATE sw_count SET swear_count = swear_count + %s WHERE name = '%s'" % (count[0],user))
			#update("UPDATE swords SET count = count + 1 WHERE name = '%s'" % user)

def process(line): 
	# first split the string up into user, and input
	userin = ""
	protocol = "PRIVMSG"
	ircout = ""
	channel = ""
	for (i, val) in enumerate(line):
		line[i] = unicode(line[i], 'utf8')

	try:
		user = line[0].split('!')[0].split(':')[1]
		channel = line[2]
		userin = ' '.join(line).split(':', 2)[2]
	except:
		user = "n/a"
	#format the return string

	#-------------------------all-logic-for-the-irc-bot-goes-here------
	if userin.startswith('.'):
		#this means that the bot is being asked something
		ircout = parsebot(user,userin)
		#need to return an array of strings here
		#for (i,val) in enumerate(ircout):
			#tmp = ""
			#for j in val:
				#tmp = tmp + "a"
			#ircout[i] = "%s %s :%s\r\n" % (protocol, CHAN, tmp)
		#print ircout
		#return ircout
	elif len(userin) > 1:
		#this is the information gathering condition
		updatebot(user,userin)
		#this can happen because we don't want to bot to return anything
		return None

	#this if statement is here to return nothing if the bot is not connected to the right channel
	if channel != CHAN:
		#return None
		return "JOIN :%s\r\n" % CHAN
	elif ircout == None: #if the bot is returning null
		return None
	rstring = "%s %s :%s\r\n" % (protocol, CHAN, ircout)
	#print rstring
	return rstring
 
s=socket.socket( ) 
s.connect((HOST, PORT)) 
s.send("NICK %s\r\n" % NICK) 
#s.send("PRIVMSG nickserv aoeuaoeu \r\n") 
s.send("USER %s %s bla :%s\r\n" % (IDENT, HOST, REALNAME)) 
#s.send("JOIN :%s\r\n" % CHAN) 
#s.send("PRIVMSG %s :%s\r\n" % (CHAN, "Hello There!")) 
s.send("PRIVMSG %s :%s\r\n" % (CHAN, "...")) 

while 1: 
        readbuffer=readbuffer+s.recv(1024) 
        temp=string.split(readbuffer, "\n") 
        readbuffer=temp.pop( ) 
 
        for line in temp:
		line=string.rstrip(line)
		line=string.split(line)
		# add logic here to parse user commands and such 
		#print ' '.join(line )
		if(line[0]=="PING"):
			s.send("PONG %s\r\n" % line[1])
		else:
			try: 
				string.decode('utf-8')	
				print "is unicode"
			except:
				retval = process(line)
				if retval != None:
					for out in retval:
						s.send(out)
