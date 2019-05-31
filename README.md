# Stepping Motor Control Webpage
利用簡單網頁控制步進電機(Adafruit-Motor-HAT with Raspberry Pi3),主網頁Webpage放置在Raspberry Pi3 
* Adafruit-Motor-HAT可以同時驅動兩個步進電機或四台DC電機,電機驅動所使用的電源必須外加電源(必根據電機5V or 12V),根據電機則外加多少電源電壓
* 安裝必要的Python library and Adafruit motor library "pip3 install Adafruit_MotorHAT"
* 安裝時可以網路連線或利用WiFi連上AP
* 進入WebPage: http://local-ip:8000
* WebPage button 有轉速高中低三種,停止,反轉/開啟

* Rraspberry pi 最好更新一下
>sudo apt-get update
>sudo apt-get upgrade
>sudo pip3 install RPI.GPIO
>sudo apt-get install python3-smbus
>sudo apt-get install python3-dev

* 第一個WebPage Control案例(先安裝庫文件) 
>sudo pip3 install Adafruit_MotorHAT
>sudo python3 ./DualWebStepper.py

* 第二個WebPage Control案例(先安裝庫文件) 
>sudo apt-get install python3-flask
>sudo python3 ./FlaskWebStepper.py
