#!/usr/bin/python
#coding=utf-8
# Install in Linux bash
# Python3 –m http.server           #
# sudo pip install simple_http_server   #?
# sudo pip3 install Adafruit_MotorHAT
#
# 20190530 update
# 
import os
import sys
import socket
import RPi.GPIO as GPIO          # Check it in your windows or Raspbian platform
#import cgi                       #CGIHTTPServer CGIHTTPRequestHandler for the post
from http.server import BaseHTTPRequestHandler, HTTPServer      # must be run python3 -m http.server   

from Adafruit_MotorHAT import Adafruit_MotorHAT
import time
import atexit
import threading
import random

# create empty threads (these will hold the stepper 1 and 2 threads)
st1 = threading.Thread()
st2 = threading.Thread()
# create a default object, no changes to I2C address or frequency
mh = Adafruit_MotorHAT()
myStepper1 = mh.getStepper(200, 1)  # 200 steps/rev, motor port #1
myStepper2 = mh.getStepper(200, 2)  # 200 steps/rev, motor port #2
myStepper1.setSpeed(6) # RPM, DC motor from 0(off) to 255(max speed), Stepper motor(usually between 60-200) 
myStepper2.setSpeed(6) # RPM, DC motor from 0(off) to 255(max speed), Stepper motor(usually between 60-200) 

# direction
stepstyles = [Adafruit_MotorHAT.SINGLE, Adafruit_MotorHAT.DOUBLE, Adafruit_MotorHAT.INTERLEAVE, Adafruit_MotorHAT.MICROSTEP]

dir = Adafruit_MotorHAT.FORWARD
#dir = Adafruit_MotorHAT.BACKWARD

# recommended for auto-disabling motors on shutdown!
def turnOffMotors():
    #mh.getStepper(0, 1).run(Adafruit_MotorHAT.RELEASE)
    #mh.getStepper(0, 2).run(Adafruit_MotorHAT.RELEASE)
    mh.getMotor(1).run(Adafruit_MotorHAT.RELEASE)
    mh.getMotor(2).run(Adafruit_MotorHAT.RELEASE)
    mh.getMotor(3).run(Adafruit_MotorHAT.RELEASE)
    mh.getMotor(4).run(Adafruit_MotorHAT.RELEASE)
atexit.register(turnOffMotors)   # 先註冊後執行(python離開時執行,防止步進電機進入卡死電流燒毀)

def stepper_worker(stepper, numsteps, direction, style):
    global stop_threads
    while stop_threads:
        stepper.step(numsteps, direction, style)

stop_threads = True
st1 = threading.Thread(target=stepper_worker, args=(myStepper1, 20, dir, stepstyles[2],))
st1.start()
st2 = threading.Thread(target=stepper_worker, args=(myStepper2, 20, dir, stepstyles[2],))
st2.start()
    
########################################################################################
########################################################################################
class MytestHTTPServer(BaseHTTPRequestHandler):
    def do_HEAD(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def _redirect(self, path):
        self.send_response(303)
        self.send_header('Content-type', 'text/html')
        self.send_header('Location', path)
        self.end_headers()

    def do_GET(self):
        html = '''
            <html>
            <body style="width:960px; margin: 20px auto;">
            <h1>The Stepping Motor Control Information</h1>
            <a href="https://louisopen.github.io">Louis Web Linking</a>
            <h3>http://louisopen.github.io</h3>
            <p>Raspberry pi3 Current GPU temperature is {}</p>
            <p><br>GPIO testting</p>
            <form action="/" method="POST">
                Turn LED :
                <input type="submit" name="submit" value="On">
                <input type="submit" name="submit" value="Off">
            </form>
            <p><br>Stepping Motor Control Dash-board</p>
            <form action="/" method="POST">
                Stepping Motor :
                <input type="submit" name="submit" value="Hi-Speed">
                <input type="submit" name="submit" value="Med-Speed">
                <input type="submit" name="submit" value="Lo-Speed">
                <input type="submit" name="submit" value="STOP">
                <input type="submit" name="submit" value="Turn-Back">
            </form>
            <p><br>User RS-485 of uart communication default setting is 9600,N,8,1</p>
            <form action="/" method="POST">
                Uart Open/Close :
                <input type="submit" name="submit" value="Open">
                <input type="submit" name="submit" value="Close">
            </form>         
            </body>
            </html>
        '''
        temp = os.popen("/opt/vc/bin/vcgencmd measure_temp").read()
        self.do_HEAD()
        self.wfile.write(html.format(temp[5:]).encode("utf-8"))

    def do_POST(self):
        global dir,st1,st2,stop_threads
        content_length = int(self.headers['Content-Length'])    # Get the size of data
        post_data = self.rfile.read(content_length).decode("utf-8")   # Get the data
        #post_data = urllib.parse.parse_qs(self.rfile.read(length).decode('utf-8'))
        post_data = post_data.split("=")[1]    # Only keep the value

        # You now have a dictionary of the post data
        print("Command is {}".format(post_data))

        # GPIO setup
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(18,GPIO.OUT)

        if post_data == 'On':
            GPIO.output(18, GPIO.HIGH)
        elif post_data == 'Off':
            GPIO.output(18, GPIO.LOW)
        elif post_data == 'Hi-Speed':
            myStepper1.setSpeed(15)
            myStepper2.setSpeed(15)

        elif post_data == 'Med-Speed':
            myStepper1.setSpeed(10)
            myStepper2.setSpeed(10)

        elif post_data == 'Lo-Speed':
            myStepper1.setSpeed(6)
            myStepper2.setSpeed(6)

        elif post_data == 'STOP':
            stop_threads = False
            turnOffMotors()
            st1.join()
            st2.join()

        else: #post_data == 'Turn-Back':
            stop_threads = False
            turnOffMotors()
            st1.join()
            st2.join()
            time.sleep(0.2)

            myStepper1.setSpeed(6)
            myStepper2.setSpeed(6)
            if dir == Adafruit_MotorHAT.FORWARD:
                dir = Adafruit_MotorHAT.BACKWARD
            else:
                dir = Adafruit_MotorHAT.FORWARD
  
            stop_threads = True
        #if not st1.isAlive():
            st1 = threading.Thread(target=stepper_worker, args=(myStepper1, 20, dir, stepstyles[2],))
            st1.start()
        #if not st2.isAlive():
            st2 = threading.Thread(target=stepper_worker, args=(myStepper2, 20, dir, stepstyles[2],))
            st2.start()

        self._redirect('/')      # Redirect back to the root url
        #self.wfile.write("You finished it".encode("utf-8"))

def getIP():
    #myname = socket.getfqdn(socket.gethostname())
    get_s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    get_s.connect(('8.8.8.8', 0))
    #ip = ('hostname: %s, localIP: %s') % (myname, get_s.getsockname()[0])
    ip = ('%s') % (get_s.getsockname()[0])
    return ip

def run():
    if sys.argv[1:]:
        host_port = int(sys.argv[1])
    else:
        host_port = 8000         # print('starting server, port', host_port)       
    host_name = getIP()          # same the localhost ip  host_name = '192.168.0.17'         
    # Server settings
    server_address = (host_name, host_port) 
    httpd = HTTPServer(server_address, MytestHTTPServer)
    #httpd = MyThreadingHTTPServer(('',8080), MytestHTTPServer)
    #httpd = MyThreadingHTTPServer(server_address, MytestHTTPServer)
    print('running server...', server_address)

    #HandlerClass.protocol_version = Protocol    # used SimpleHTTPRequestHandler
    #httpd = ServerClass(server_address, HandlerClass) #used default server class
    #sa = httpd.socket.getsockname()
    #print "Serving HTTP on", sa[0], "port", sa[1], "..."

    httpd.serve_forever()

if __name__ == '__main__': 
    run()