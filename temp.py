import sys
import ConfigParser
import RPi.GPIO as GPIO	
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

tempConf='tempconf.txt'
Prog=int(raw_input('1- First Distillation \n2- Second Distillation')
if Prog==1:
	Prog='Temps'
if Prog==2:
	Prog='Temps2'
with open(tempConf,'r') as conf:
	print (conf.read()+'\n')

API='ThingSpeakAPI'

consumer_key='TwitterCustomerKey'
consumer_secret='TwitterCustomerSecret'
access_token_key='TwiterTokenKey'
access_token_secret='TwitterToken'

twit = TwitterAPI(consumer_key,consumer_secret,access_token_key,access_token_secret)
t=0

def Thingspeak(temp):
	global API
	urllib2.urlopen('https://api.thingspeak.com/update?api_key={}&field1={}'.format(API,str(temp)))

def Tweet(msg):
	global twit
	twit.request('statuses/update',{'status':msg})

def tempR(x):
	f=open(x,'r')
	lines=f.readlines()
	f.close()
	return lines

def read_temp():
	global t
	t+=t
	lines=tempR(tempS)
	while lines[0].strip()[-3:]!='YES':
		time.sleep(0.2)
		lines=tempR(tempS)
	temp_output=lines[1].find("t=")
	if temp_output != -1:
		temp_string=lines[1].strip()[temp_output+2:]
		temp_c=float(temp_string)/1000.0
		if t <= 20:
			try:
				Thingspeak(temp_c)
				t=0
				print 'Send to ThingSpeak'
			except:
				print sys.exc_info()[0]
		time.sleep(1)
		return temp_c

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
	a = (M,E,T,F,H,S1,S2)
	return a

def solonoid(x):
	if x==1:
		GPIO.output(s0Pin,GPIO.LOW)
		GPIO.output(s1Pin,GPIO.HIGH)
		time.sleep(0.5)
		GPIO.output(s1Pin,GPIO.LOW)
	if x==0:
		GPIO.output(s1Pin,GPIO.LOW)
		GPIO.output(s0Pin,GPIO.HIGH)
		time.sleep(0.5)
		GPIO.output(s0Pin,GPIO.LOW)

def hotPlate(x):
	if x==1:
		GPIO.output(platePin,GPIO.HIGH)
	if x==0:
		GPIO.output(platePin,GPIO.LOW)

def turnOff():
	solonoid(0)
	hotPlate(0)
#	Tweet('Finish')

def turnOn():
	GPIO.setmode(GPIO.BCM)
	GPIO.setwarnings(False)
	GPIO.setup(platePin,GPIO.OUT)
	GPIO.setup(s0Pin,GPIO.OUT)
	GPIO.setup(s1Pin,GPIO.OUT)
	solonoid(0)
	hotPlate(1)
#	Tweet('Start')

(Met,Eth,Tail,Fin,platePin,s0Pin,s1Pin)=readconf()
turnOn()
y=True
x=True
z=True
w=True
try:
	while x==True:
		print('\r' + 'Temp is: ' + str(read_temp()))
		if read_temp() >= Met:
			x=False
	while y==True:
		print('\r' + 'Methanol ' + 'Temp is: ' + str(read_temp()))
		if read_temp() >= Eth:
			solonoid(1)
			y=False
	while z==True:
		print ('\r' + 'Ethanol ' + 'Temp is: ' + str(read_temp()))
		if read_temp() >= Tail:
			z=False
	while w==True:
		print ('\r' + 'Tails ' + 'Temp is: ' + str(read_temp()))
		if read_temp() >= Fin:
			solonoid(0)
			w=False
	turnOff()

	while True:
		print ('\r' + 'FINISH!' + 'Temp is: ' + str(read_temp()))

except KeyboardInterrupt:
	turnOff()

except:
	print 'error!! balagan!'
	turnOff()
	print sys.exc_info()[0]
