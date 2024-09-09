'''
Control the Brightness of LED using PWM on Raspberry Pi
http://www.electronicwings.com
'''

import RPi.GPIO as GPIO
from time import sleep

# gpio setup
# setting the numbering system for subsequent calls that reference pins
# this corresponds to the gpio pins. i.e. the number after "gpio" on the pinout diagram
GPIO.setmode(GPIO.BCM)
# disabling warnings cause we dont like that stuff :D
GPIO.setwarnings(False)


# setting the pin we are going to use for testing (GPIO 18 PWM0)
# on a side note, the Pi4B has two pairs of PWM channels:
# PWM0_0 - gpio 12, 18, and 52
# PWM0_1 - gpio 13, 19, 45, and 53
# PWM1_0 - gpio 40
# PWM1_1 - gpio 41
# however, only gpio pins 12, 13, 18, and 19 are on the 40 pin header, so we really
# only have 2 PWMs that are usable
pwmPin = 18


# setting up pin output
GPIO.setup(pwmPin, GPIO.OUT)

# setting up the PWM frequency (1k) and duty cycle (0 = off)
pwmObj = GPIO.PWM(pwmPin, 50)
pwmObj.start(15)

print('CVHS PWM Testing Shell:')
print('\t- Please enter an integer [0, 100] to set the duty cycle')
print('\t- Enter "exit" to quit')
print('---------------------------------------------------------------------------------')

done = False
while not done:
	rslt = input('\t# ')

	splitRslt = rslt.split(', ')

	if rslt == 'exit':
		done = True
		continue

	else:
		try:
			dutyCycle = float(rslt)
		except:
			print(f'\t\t{rslt} is not a valid command. Please try again.')
			continue

		if dutyCycle < 0 or dutyCycle > 100:
			print('\t\tPlease enter a number [0, 100]')
			continue

		pwmObj.ChangeDutyCycle(dutyCycle)

print('Exiting pseudo shell...')