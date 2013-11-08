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
sweardict = ["fuck", "shit", "bollocks","cunt","balls"]
conn = sqlite3.connect("ircbot.db") 

#--------------------------------------database-----------------------------
def database():
	cursor = conn.cursor()
	return cursor

def update(query):
	database().execute(query)
	conn.commit()


def queryone(query):
	cursor = database()
	cursor.execute(query)

	return cursor.fetchone()

def queryall(query):
	cursor = database()
	cursor.execute(query)

	all_rows = cursor.fetchall()
	for row in all_rows:
		print('{0} : {1}'.format(row[0], row[1]))
#----------------------------------end-database-----------------------------

def parsebot(user, userin):
	#this is where all the heavy lifting is!
	inlist = userin.split(' ')
	q = inlist[0]
	command = q.split('.')[1]
	tail = ' '.join(inlist[1:])
	if q == ".myswears":
		ret = queryone("Select * from sw_count where name = '%s'" % user)
		if ret == None:
			return None
		return "%s: %s swears" % (ret[0], ret[1])
	elif q == ".hello":
		return "hello %s" % user
	elif q == ".slap":
		return "%s slaps %s" % (user, tail)
	elif q == ".addsw":
		#adds a swear word to the list
		update("INSERT INTO swords values('%s', 0)")
	else:
		return "%s %ss %s" % (user, command, tail)
def updatebot(user, userin):
	#this doesn't return anything, but does things like update the swear count
	#add user to the database if needed
	try:
		out = queryone("Select * from sw_count where name = '%s'" % user)
		if out == None:
			update("INSERT INTO sw_count values('%s', 0)" % user)
	except:
		update("INSERT INTO sw_count values('%s', 0)" % user)

	#this needs to check if a user uses a swear word
	#read swear words from the database
	for sw in sweardict:
		if sw in userin:
			#add a swear to the database
			update("UPDATE sw_count SET swear_count = swear_count + 1 WHERE name = '%s'" % user)

def process(line): 
	# first split the string up into user, and input
	userin = ""
	protocol = "PRIVMSG"
	ircout = ""
	channel = ""
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
	elif len(userin) > 1:
		#this is the information gathering condition
		updatebot(user,userin)
		#this can happen because we don't want to bot to return anything
		return None


	#this if statement is here to return nothing if the bot is not connected to the right channel
	if channel != CHAN:
		#return None
		return "JOIN :%s\r\n" % CHAN
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
#s.send("PRIVMSG %s :%s\r\n" % (CHAN, "I am a bot")) 

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
			retval = process(line)
			if retval != None:
				s.send(process(line))
