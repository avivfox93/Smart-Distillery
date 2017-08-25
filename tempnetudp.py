

import ConfigParser
import select
import threading
import socket
import urllib2
import os
import time
from TwitterAPI import TwitterAPI

os.system("modprobe w1-gpio")
os.system("modprobe w1-therm")
def findSensor(name,name2,path):
	for root,dirs,files in os.walk(path):
		if name in dirs:
			a=os.path.join(root,name)
			print a
			return a
		elif name2 in dirs:
			a=os.path.join(root,name2)
			print a
			return a
		else:
			print 'cant find sensor!'
			exit()

tempName2='28-0000071f2750'
tempName='28-0416589a15ff'
tempSensorDir='/sys/bus/w1/devices/'
tempS='{}/w1_slave'.format(findSensor(tempName,tempName2,tempSensorDir))

API='58IQN3JJRCHEP7MP'

consumer_key='hT4p0SU4SRa1e6dJTbzH0g3S7'
consumer_secret='ez1bjqsDe6zjCebny4yfM3IgSyjefq14LlaIDtCeiFSByuYDhT'
access_token_key='767014581872889856-98h9sokFGq5YBH4hZysHHAOpm1rrPYr'
access_token_secret='MwqLKNVrQrQBAU3kLbEBVNi4D6UEQVM6VAH1Q3yQaDXEW'

t = TwitterAPI(consumer_key,consumer_secret,access_token_key,access_token_secret)
temp = ''
s=''
s1=''
cnct = 0
a=socket.socket(AF_INET, SOCK_DGRAM)
clients=[]
a.settimeout(2)

try:
	a.bind(('0.0.0.0',5657))
	a.listen(5)
except:
	print 'error connecting...'


tempConf='tempconf.txt'

Prog=int(raw_input('1- First Distillation \n2- Second Distillation'))
if Prog==1:
	Prog='Temps'
if Prog==2:
	Prog='Temps2'
with open(tempConf,'r') as conf:
	print (conf.read()+'\n')


with open(tempConf,'r') as conf:
        print (conf.read()+'\n')



def tempR():
	f=open(tempS,'r')
	lines=f.readlines()
	f.close()
	return lines

def read_temp():
	lines=tempR()
	while lines[0].strip()[-3:]!='YES':
		time.sleep(0.2)
		lines=tempR()
	temp_output=lines[1].find("t=")
	if temp_output != -1:
		temp_string=lines[1].strip()[temp_output+2:]
		temp_c=float(temp_string)/1000.0
		return temp_c

def sock(tmp):
	while len(clients)<1:
		print " waiting for connection....."
		newMsg,newClient = a.recvfrom(1024)
		clients.append(newClient)
		sendto("/c/"+1,newClient)
		print "connected succesfully!"
		
	newMsg,newClient = a.recvfrom(1024)
	print "recived:  " + newMsg
	if any(for x in clients if x == newClient) !=True:
		clients.append(newClient)
		sendto("/c/"+1,newClient)
	if newMsg == "help":
		sendto(str(redconf),newClient)
	if newMsg == "bye":
		clients.remove(newClient)
	for i in clients:
		sendto(tmp + "\n",i)
		print "MSG sent to " + i

def readconf():
        configParser = ConfigParser.RawConfigParser()
        configParser.readfp(open(tempConf))
        M = float(configParser.get(Prog,'Met'))
        E = float(configParser.get(Prog,'Eth'))
        T = float(configParser.get(Prog,'Tails'))
        F = float(configParser.get(Prog,'Fin'))
        H = int(configParser.get('Pins','Hotplate'))
        S1= int(configParser.get('Pins','Solonoid1'))
        S2= int(configParser.get('Pins','Solonoid2'))
        a = (M,E,T,F)
        return a
(Met,Eth,Tails,Fin)=readconf()
x=0
y=0
z=0
w=0
while True:
	try:
		global temp
		temp= str(read_temp())
		print('\r' + 'Temp is: ' + temp)
		time.sleep(2)
		if float(temp)>=Met:
			if x<2:
				sock("MET")
				x=x+1
		if float(temp)>=Eth:
			if z<2:
				sock("ETH")
				z=z+1
		if float(temp)>=Tails:
			if w<2:
				sock("TAILS")
				w=w+1
		if float(temp)>Fin:
			if y<2:
				sock ("FIN")
				y=y+1
		sock(temp)
	except KeyboardInterrupt:
		a.close()
		print 'connection closed \nclosing program'
		exit()