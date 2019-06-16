#!/bin/sh
#This bash called by /home/pi/.config/autostart/autoboot.desktop
#Git clone https://github.com/louisopen/SteppingMotorWeb
#cd SteppingMotorWeb
#tr -d "\r" < oldname.sh > newname.sh   #if you can't cd to .... just do it.
jump_dir=/home/pi/SteppingMotorWeb
cd $jump_dir
sudo python3 $jump_dir/DualStepperWeb.py
#sudo python3 $jump_dir/FlaskWebStepper.py
pwd
exit 0
