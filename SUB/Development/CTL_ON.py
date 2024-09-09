'''
CTL_ON.py

Intakes control signal from ctl_recieve and sends to GPIO when enabled

Copyright (c) 2023
Created by Christopher Holm
holmch@oregonstate.edu

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

Revision History
#####################################################################################
2023/01/08 CEH Initial Version


####################################################################################
'''
#!/usr/bin/python3
# Define Libraries
import RPi.GPIO as GPIO
from subprocess import Popen, PIPE
import signal
import time

# Define GPIO
# Pin Definitions:
ch1Pin = 12  # Broadcom pin 12 (Pi Pin 32)
ch2Pin = 13  # Broadcom pin 13
ch3Pin = 16  # Broadcom pin 16
ch4Pin = 17  # Broadcom pin 17
ch5Pin = 22  # Broadcom pin 22
ch6Pin = 23  # Broadcom pin 23
ch7Pin = 24  # Broadcom pin 24
ch8Pin = 25  # Broadcom pin 25
lightPin = 5  # Broadcom pin 5

# Duty cycle (0-100) for PWM pin
dc1 = dc2 = dc3 = dc4 = dc5 = dc6 = dc7 = dc8 = 50
lightdc = 0
# Pin Setup:
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)  # Broadcom pin-numbering scheme

# PWM pins set as output
GPIO.setup(ch1Pin, GPIO.OUT)
GPIO.setup(ch2Pin, GPIO.OUT)
GPIO.setup(ch3Pin, GPIO.OUT)
GPIO.setup(ch4Pin, GPIO.OUT)
GPIO.setup(ch5Pin, GPIO.OUT)
GPIO.setup(ch6Pin, GPIO.OUT)
GPIO.setup(ch7Pin, GPIO.OUT)
GPIO.setup(ch8Pin, GPIO.OUT)
GPIO.setup(lightPin, GPIO.OUT)

# Initialize PWM on pwmPins
pwm1 = GPIO.PWM(ch1Pin, 333)
pwm2 = GPIO.PWM(ch2Pin, 333)
pwm3 = GPIO.PWM(ch3Pin, 333)
pwm4 = GPIO.PWM(ch4Pin, 333)
pwm5 = GPIO.PWM(ch5Pin, 333)
pwm6 = GPIO.PWM(ch6Pin, 333)
pwm7 = GPIO.PWM(ch7Pin, 333)
pwm8 = GPIO.PWM(ch8Pin, 333)
pwmlight = GPIO.PWM(lightPin, 333)
pwm1.start(dc1)
pwm2.start(dc2)
pwm3.start(dc3)
pwm4.start(dc4)
pwm5.start(dc5)
pwm6.start(dc6)
pwm7.start(dc7)
pwm8.start(dc8)
pwmlight.start(lightdc)

lights = False
fwdbk = 0
rotate = 0
updwn = 0
roll = 0


# Map Logitech F310 button and joystick events
button_mappings = {
    "1": fwdbk,
    "0": rotate,
    "4": updwn,
    "3": roll,
    "BTN_THUMBL": "enable",
    "BTN_Y": "lights",
    "BTN_TL": "dim",
    "BTN_TR": "bright"
}

def cleanup_and_exit(signum, frame):
    print("Received SIGTERM, Control has been disabled, closing out")
    for pwm in [pwm1, pwm2, pwm3, pwm4, pwm5, pwm6, pwm7, pwm8, pwmlight]:
        pwm.stop()
    GPIO.cleanup()

def process_event(event):
    if event.startswith("AXIS"):
        axis, value = event.split()[1], event.split()[2]
        if axis in button_mappings:
            control_name = button_mappings[event_code]
            control_value = value
        print(f"Event Axis {axis}, {value}")
    else:
        event_code = event
        if event_code in button_mappings:
            control_name = button_mappings[event_code]
            control_value = 1  # You may want to change this based on your specific needs
            apply_control(control_name, control_value)

def get_button_state(button):
    try:
        # Assume ctl_receive.py prints the button input
        process = Popen(["python3", "ctl_receive.py", button], stdout=PIPE, stderr=PIPE)
        output, _ = process.communicate()
        return int(output.decode().strip())
    except Exception as e:
        print(f"Error getting button state: {e}")
        return 0

def apply_control(control_name, control_value):
    global fwdbk, rotate, updwn, roll, enable, lights, dim, bright

    if control_name == "fwdbk":
        fwdbk = map_range(control_value, -32768, 32767, 0, 100)
        pwm1.start(fwdbk)
        pwm4.start(fwdbk)
        print(f"setting pwm1 and pwm4 to {fwdbk}")
    elif control_name == "rotate":
        rotate = map_range(control_value, -32768, 32767, 0, 100)
        if rotate > 50:
            dc4 = ((rotate - 50) / 2) + 50
            dc1 = abs(((rotate - 50) / 2) - 50)
        elif rotate < 50:
            dc1 = ((50 - rotate) / 2) + 50
            dc4 = abs(((50 - rotate) / 2) - 50)
        else:
            dc1 = dc4 = 50
        pwm1.start(dc1)
        pwm4.start(dc4)
        print (f"Setting pwm1 to {dc1} and pwm4 to {dc4}")
    elif control_name == "updwn":
        updwn = map_range(control_value, -32768, 32767, 0, 100)
        pwm2.start(updwn)
        pwm3.start(updwn)
        print(f"Setting pwm2 and pwm3 to {updwn}")
    elif control_name == "roll":
        roll = map_range(control_value, -32768, 32767, 0, 100)
        if roll > 50:
            dc2 = ((rotate - 50) / 2) + 50
            dc3 = abs(((rotate - 50) / 2) - 50)
        elif roll < 50:
            dc3 = ((rotate - 50) / 2) + 50
            dc2 = abs(((rotate - 50) / 2) - 50)
        else:
            dc2 = dc3 = 50
        pwm2.start(dc2)
        pwm3.start(dc3)
        print(f"Setting pwm2 to {dc2} and pwm3 to {dc3}")
    elif control_name == "enable":
        # I think this just needs to be ignored here, but will keep it here in case I change my mind
        print("Enable Received, make this do something.....")
        pass
    elif control_name == "lights":
        if control_value == 1:
            lights = not lights
            if lights:
                pwmlight.start(lightdc)
                print(f"Turning on Lights at {lightdc}")
            else:
                pwmlight.stop()
                print("Lights out!")
        else:
            print("light input error?")
    elif control_name == "dim":
        if control_value == 1:
            if lightdc > 10:
                lightdc = lightdc - 10
                pwmlight.start(lightdc)
                print(f"Setting Lights Dimmer by 10 now set to {lightdc}")
            else:
                print("Lights already at minimum setting, no change")
    elif control_name == "bright":
        if control_value == 1:
            if lightdc < 100:
                lightdc = lightdc + 10
                pwmlight.start(lightdc)
                print(f"Setting Lights Brighter by 10 now set to {lightdc}")
            else:
                print("Lights already at maximum setting, no change")

def map_range(value, in_min, in_max, out_min, out_max):
    return (value - in_min) * (out_max - out_min) // (in_max - in_min) + out_min

try:
    signal.signal(signal.SIGTERM, cleanup_and_exit)

    ctl_receive_process = Popen(["python3", "ctl_receive.py"], stdout=PIPE, stderr=PIPE)

    while True:
        # Read button input from ctl_receive.py
        output, _ = ctl_receive_process.communicate()
        button_input = output.decode().strip()

        if button_input:
            process_event(button_input)
            print(f"Received: {button_input}")
        time.sleep(0.01)  # Adjust the sleep duration based on your requirements

except KeyboardInterrupt:
    pass
finally:
    # Ensure cleanup before exit
    cleanup_and_exit(None, None)