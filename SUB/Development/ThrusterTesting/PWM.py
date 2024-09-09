'''
Control of CVHS ROV THRUSTERS
Version 1.0.0 created 2023/11/15
By Chris Holm
holmch@oregonstate.edu
#################################################################
Revision History
2023-11-15 CEH Initial Version


##################################################################
'''
#!/usr/bin/python3
-

# External Module imports time
from time import sleep
import RPi.GPIO as GPIO

# Pin Definitions:
ch1Pin = 12  # Broadcom pin 12 (Pi Pin 32)
ch2Pin = 13  # Broadcom pin 13
ch3Pin = 16  # Broadcom pin 16
ch4Pin = 17  # Broadcom pin 17
ch5Pin = 22  # Broadcom pin 22
ch6Pin = 23  # Broadcom pin 23
ch7Pin = 24  # Broadcom pin 24
ch8Pin = 25  # Broadcom pin 25
lightPin = 5 # Broadcom pin 5

# duty cycle (0-100) for PWM pin
dc1 = 50
dc2 = 50
dc3 = 50
dc4 = 50
dc5 = 50
dc6 = 50
dc7 = 50
dc8 = 50
lightdc = 50


# Pin Setup:
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)         # Broadcom pin-numbering scheme
# PWM pins set as output
GPIO.setup(ch1Pin,GPIO.OUT)
GPIO.setup(ch2Pin,GPIO.OUT)
GPIO.setup(ch3Pin,GPIO.OUT)
GPIO.setup(ch4Pin,GPIO.OUT)
GPIO.setup(ch5Pin,GPIO.OUT)
GPIO.setup(ch6Pin,GPIO.OUT)
GPIO.setup(ch7Pin,GPIO.OUT)
GPIO.setup(ch8Pin,GPIO.OUT)
GPIO.setup(lightPin,GPIO.OUT)
# Initialize PWM on pwmPins

pwm1 = GPIO.PWM(ch1Pin,1500)
pwm2 = GPIO.PWM(ch2Pin,1500)
pwm3 = GPIO.PWM(ch3Pin,1500)
pwm4 = GPIO.PWM(ch4Pin,1500)
pwm5 = GPIO.PWM(ch5Pin,1500)
pwm6 = GPIO.PWM(ch6Pin,1500)
pwm7 = GPIO.PWM(ch7Pin,1500)
pwm8 = GPIO.PWM(ch8Pin,1500)
pwmlights = GPIO.PWM(lightPin,1500)

pwm1.start(100)
pwm2.start(100)
pwm3.start(100)
pwm4.start(100)
pwm5.start(100)
pwm6.start(100)
pwm7.start(100)
pwm8.start(100)
pwmlights.start(100)

input('Press return to stop:')   # use raw_input for Python 2
pwm1.stop()
pwm2.stop()
pwm3.stop()
pwm4.stop()
pwm5.stop()
pwm6.stop()
pwm7.stop()
pwm8.stop()
pwml.stop()
GPIO.cleanup()

#
