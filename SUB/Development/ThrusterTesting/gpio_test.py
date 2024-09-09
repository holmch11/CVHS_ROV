import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)
GPIO.setup(12, GPIO.OUT)

p = GPIO.PWM(12,1500) # channel=12 , frequency=0.5Hz
p.start(20)
input('Press return to stop:')   # use raw_input for Python 2
p.stop()
GPIO.cleanup()
