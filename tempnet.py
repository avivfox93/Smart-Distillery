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

tempName='28-0000071f2750'
tempName2='28-0416589a15ff'
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
a=socket.socket()
open_client_sockets=[]

try:
	a.bind(('0.0.0.0',5657))
	a.listen(5)
except:
	print 'error connecting...'


tempConf='tempconf.txt'

Prog=int(raw_input('1- First Distillation \n2- Second Distillation')
if Prog==1:
	Prog='Temps'
if Prog==2:
	Prog='Temps2'
with open(tempConf,'r') as conf:
	print (conf.read()+'\n')


with open(tempConf,'r') as conf:
        print (conf.read()+'\n')

def send():
	while True:
		print 'sending'
		global a
		global s
		global s1
		global temp
		try:
			if accpt()!=False:
				s.send(temp+'n')
			else:
				pass
		except:
			pass
		time.sleep(5)
def accpt():
	global cnct
	global a
	global s
	global s1
	try:
		(s,s1)=a.accept()
		return True
	except:
		return False

def Thingspeak(temp):
	global API
	a=urllib2.urlopen('https://api.thingspeak.com/update?api_key={}&field1={}'.format(API,str(temp)))

def Tweet(msg):
	global t
	t.request('statuses/update',{'status':msg})

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
	rlist,wlist,xlist=select.select([a]+open_client_sockets,open_client_sockets,[])
	for current_socket in rlist:
		if current_socket is a:
			(new_socket,address) = a.accept()
			open_client_sockets.append(new_socket)
			print ('got connection from: ' + str(address))
			new_socket.send('Shalom!\n')
		else:
			data= current_socket.recv(1024)
			print data
			if data.find('bye')==0:
				open_client_sockets.remove(current_socket)
				print (str(current_socket) + '\n disconnected')
			if data.find('help')==0:
				print ('got help message from: '+ str(current_socket))
				try:
					current_socket.send(readconf())
				except:
					print 'faild to send TempConf'
	for current_socket in wlist:
		try:
			current_socket.send(tmp+'\n')
			print 'massage sent'
		except:
			print 'faild send massage...samak!'
			open_client_sockets.remove(current_socket)
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
