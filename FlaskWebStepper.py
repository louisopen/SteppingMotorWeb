#!/usr/bin/env python
#coding:utf-8
from flask import Flask
from flask import request
from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_DCMotor

import time
import atexit
import sys, socket
import threading

app = Flask(__name__)
myname = socket.getfqdn(socket.gethostname())

mh = Adafruit_MotorHAT(addr=0x60)
myMotor1 = mh.getStepper(200, 1)
myMotor2 = mh.getStepper(200, 2)
myMotor1.setSpeed(15)
myMotor2.setSpeed(15)
#myMotor.run(Adafruit_MotorHAT.FORWARD)   #has no attribute 'run'
#myMotor.run(Adafruit_MotorHAT.RELEASE)   #has no attribute 'run'
# direction
stepstyles = [Adafruit_MotorHAT.SINGLE, Adafruit_MotorHAT.DOUBLE, Adafruit_MotorHAT.INTERLEAVE, Adafruit_MotorHAT.MICROSTEP]
dir = Adafruit_MotorHAT.FORWARD     #"+"
#dir = Adafruit_MotorHAT.BACKWARD

def turnOffMotors():
    mh.getMotor(1).run(Adafruit_MotorHAT.RELEASE)
    mh.getMotor(2).run(Adafruit_MotorHAT.RELEASE)
    mh.getMotor(3).run(Adafruit_MotorHAT.RELEASE)
    mh.getMotor(4).run(Adafruit_MotorHAT.RELEASE)
atexit.register(turnOffMotors)

def stepper_worker(stepper, numsteps, direction, style):
    global stop_threads
    while stop_threads:
        stepper.step(numsteps, direction, style)

stop_threads = True
st1 = threading.Thread(target=stepper_worker, args=(myMotor1, 20, dir, stepstyles[2],))
st1.start()
st2 = threading.Thread(target=stepper_worker, args=(myMotor2, 20, dir, stepstyles[2],))
st2.start()


@app.route("/")
def web_interface():
    html = open("web_interface.html")
    response = html.read().replace('\n', '')
    html.close()

    global stop_threads
    stop_threads = False
    turnOffMotors()         #STOP
    st1.join()
    st2.join()
    return response
    
#@app.route("/set_speed", methods=['GET', 'POST'])    
@app.route("/set_speed")
def set_speed():
    global dir, st1, st2, stop_threads, stepstyles, stepper_worker
    speed = request.args.get("speed")   #取得網頁設定的speed"值"
    #print ("Received " + str(speed))
    if int(speed) == 0:
        stop_threads = False
        turnOffMotors()     #STOP all
        st1.join()
        st2.join()
        return "Received " + str(speed)
        
    if int(speed) < 0:      #"-"
        dir = Adafruit_MotorHAT.BACKWARD
    else:
        dir = Adafruit_MotorHAT.FORWARD

    #print ("Direction " + str(dir))
    #myMotor = mh.getStepper(20, 1)

    stop_threads = True
    if not st1.isAlive():       #Motor停止再改變方向否則無法換相
        st1 = threading.Thread(target=stepper_worker, args=(myMotor1, 20, dir, stepstyles[2],))
        st1.start()
    else:
        myMotor1.step(20, dir, stepstyles[2])
    if not st2.isAlive():
        st2 = threading.Thread(target=stepper_worker, args=(myMotor2, 20, dir, stepstyles[2],))
        st2.start() 
    else:
        myMotor2.step(20, dir, stepstyles[2])
    myMotor1.setSpeed(abs(int(speed)))   #速度沒有"負"值, 轉動方向
    myMotor2.setSpeed(abs(int(speed)))   #速度沒有"負"值, 轉動方向
    return "Received " + str(speed)



def getIP():
    get_s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    get_s.connect(('8.8.8.8', 0))
    #ip = ('hostname: %s, localIP: %s') % (myname, get_s.getsockname()[0])
    ip = ('%s') % (get_s.getsockname()[0])
    return ip

if __name__ == "__main__":
    if sys.argv[1:]:
        host_port = int(sys.argv[1])
    else:
        host_port = 5000         # print('starting server, port', host_port)       
    host_name = getIP()          # same the localhost ip  host_name = '192.168.0.17'
    print(myname)
    
    #app.debug = True
    app.run(host=host_name, port=host_port, debug=False)
    