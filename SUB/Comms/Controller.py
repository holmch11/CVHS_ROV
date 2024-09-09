'''
Controller.py

Receives Controller input from Control at 192.168.2.2:5800
This script is started by Controller_enable.py and gets controller data from ctl_receive.py
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
2023/12/05 CEH Initial Version


####################################################################################
'''
#!/usr/bin/python3
# Define Libraries
import RPi.GPIO as GPIO
import signal
import time
import socket
import threading
import serial
import re

# Define GPIO
# Pin Definitions:
lightPin = 12  # Broadcom pin 32

# Duty cycle (0-100) for PWM pin
dc1 = dc2 = dc3 = dc4 = 50
lightdc = 60

# Pin Setup:
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)  # Broadcom pin-numbering scheme
ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)

# PWM pins set as output
GPIO.setup(lightPin, GPIO.OUT)

# Initialize PWM on pwmPins
pwmlight = GPIO.PWM(lightPin, 332)
pwmlight.start(lightdc)

enable = False
lights = False
fwdbk = 0
rotate = 0
updwn = 0
roll = 0
client_socket = None
stop_threads = False
UDP_IP = "192.168.2.2"
UDP_PORT = 5650  # Battery output port
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


def apply_control(control_name, control_value):
    global fwdbk, rotate, updwn, roll, enable, lights, lightdc, dim, bright
    if control_name == "enable":
        enable = not enable
        if enable == True:
            print("Enable Received")
            sock.sendto("Enable Received".encode('utf-8'), (UDP_IP, UDP_PORT))
        else:
            print("Control Soft Disabled On")
            sock.sendto("Soft Disable On".encode('utf-8'), (UDP_IP, UDP_PORT))
    if enable == True:
        if control_name == "fwdbk":
            fwdbk = map_range(control_value, -32768, 32767, 100, 0)
            print(f"setting pwm1 and pwm4 to {fwdbk}")
            serialData = f"pwm1:{fwdbk},pwm4:{fwdbk}\n"
            ser.write(serialData.encode('utf-8'))
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
            print(f"Setting pwm1 to {dc1} and pwm4 to {dc4}")
            serialData = f"pwm1:{dc1},pwm4:{dc4}\n"
            ser.write(serialData.encode('utf-8'))
        elif control_name == "updwn":
            updwn = map_range(control_value, -32768, 32767, 0, 100)
            print(f"Setting pwm2 and pwm3 to {updwn}")
            serialData = f"pwm2:{updwn},pwm3:{updwn}\n"
            ser.write(serialData.encode('utf-8'))
        elif control_name == "roll":
            roll = map_range(control_value, -32768, 32767, 0, 100)
            if roll > 50:
                dc2 = ((roll - 50) / 2) + 50
                dc3 = abs(((roll - 50) / 2) - 50)
            elif roll < 50:
                dc3 = ((50 - roll) / 2) + 50
                dc2 = abs(((50 - roll) / 2) - 50)
            else:
                dc2 = dc3 = 50
            print(f"Setting pwm2 to {dc2} and pwm3 to {dc3}")
            serialData = f"pwm2:{dc2},pwm3:{dc3}\n"
            ser.write(serialData.encode('utf-8'))
        elif control_name == "lights":
            if control_value == 1:
                lights = not lights
                if lights == True:
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
    else:
        print("Soft Disable Active")
        pass


def map_range(value, in_min, in_max, out_min, out_max):
    return (value - in_min) * (out_max - out_min) // (in_max - in_min) + out_min


def is_server_alive():
    try:
        # Send a small request to check if the server is alive
        client_socket.sendall(b"PING")
        return True
    except Exception:
        return False


def cleanup_and_exit(signum, frame):
    global stop_threads
    print("Received SIGTERM, Control has been disabled, closing out")
    stop_threads = True  # Set the flag to stop threads
    pwmlight.stop()
    GPIO.cleanup()
    ser.close()
    sock.close()


def process_event(event):
    if event.startswith("AXIS"):
        axis, value = event.split()[1], int(event.split()[2])  # Convert value to integer
        if axis == "1":
            apply_control("fwdbk", value)
        elif axis == "3":
            apply_control("rotate", value)
        elif axis == "4":
            apply_control("updwn", value)
        elif axis == "0":
            apply_control("roll", value)
        print(f"Event Axis {axis}, {value}")
    if event.startswith("BUTTON"):
        if "BTN_THUMBL" in event and "1" in event:
            apply_control("enable", 1)
        elif "BTN_WEST" in event and "1" in event:
            apply_control("lights", 1)
        elif "BTN_TL" in event and "1" in event:
            apply_control("dim", 1)
        elif "BTN_TR 1" in event and "1" in event:
            apply_control("bright", 1)
    else:
        print("Button has no function map")


def controller_thread():
    global client_socket, stop_threads

    try:
        while not stop_threads:
            data = client_socket.recv(1024)
            if not data:
                break

            button_input = data.decode().strip()
            process_event(button_input)
            print(f"Received: {button_input}")

            time.sleep(0.01)  # Adjust the sleep duration based on your requirements

            # Check if the server is still alive
            if not is_server_alive():
                print("Server is no longer reachable. Exiting.")
                stop_threads = True

    except Exception as e:
        print(f"An unexpected error occurred in controller_thread: {e}")


def serial_thread():
    global stop_threads

    try:
        last_battery_voltage_time = time.time()

        while not stop_threads:
            # Read data from the serial port
            serial_data = ser.readline().decode('utf-8').strip()

            if serial_data:
                print(serial_data)

                # Check for "Battery Voltage" in the serial data
                if "Battery Voltage" in serial_data:
                    # Check if it's been one second since the last battery voltage update
                    if (time.time() - last_battery_voltage_time) >= 1:
                        # Update the last update time
                        last_battery_voltage_time = time.time()

                        # Extract battery voltage using a regular expression
                        match = re.search(r'Battery Voltage: ([\d.]+)', serial_data)
                        if match:
                            voltage_str = match.group(1)
                            try:
                                battery_voltage = float(voltage_str)
                                sock.sendto(str(battery_voltage).encode('utf-8'), (UDP_IP, UDP_PORT))
                            except ValueError:
                                print("Failed to parse battery voltage")

                time.sleep(0.01)  # Adjust the sleep duration based on your requirements

    except Exception as e:
        print(f"An unexpected error occurred in serial_thread: {e}")


def main():
    global client_socket, stop_threads  # Declare client_socket as a global variable

    server_address = "192.168.2.2"
    server_port = 5800

    # Connect to the server
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_address, server_port))
    print(f"Connected to server at {server_address}:{server_port}")
    time.sleep(5)
    try:
        # Start the controller_thread in the background
        controller_thread_instance = threading.Thread(target=controller_thread)
        controller_thread_instance.start()
        serial_thread_instance = threading.Thread(target=serial_thread)
        serial_thread_instance.start()
        while not stop_threads:
            time.sleep(1)  # Adjust the sleep duration based on your requirements

            # Check if the server is still alive
            if not is_server_alive():
                print("Server is no longer reachable. Exiting.")
                stop_threads = True
    finally:
        client_socket.close()
        cleanup_and_exit(None, None)
        sock.close()


if __name__ == "__main__":
    try:
        signal.signal(signal.SIGTERM, cleanup_and_exit)
        main()  # Run the main script logic without threading

    except KeyboardInterrupt:
        pass
    finally:
        # Ensure cleanup before exit
        cleanup_and_exit(None, None)
