'''
Controller_enable.py

Recieves Enable button input  at 192.168.2.2:5840

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
2023/01/05 CEH Initial Version
2024/03/07 CEH Removed GPIO and added better process handling, ensure we don't Zombie!

####################################################################################
'''
import socket
import os
import subprocess
from subprocess import PIPE
import psutil
import time
import serial
import threading

# Server configuration
host = "192.168.2.3"
client = "192.168.2.2"
control_port = 5640
data_port = 5650
serial_port = "/dev/ttyACM0"
baud_rate = 115200
process = None
ser = None
serial_running = False
broadcast_enabled = True  # Global flag to control the broadcast thread
battery_broadcast_thread = None

def start_controller():
    global process
    log_dir = "/home/rov/logs/"
    script_dir = "/home/rov/CVHS_SUB/Comms/Controller.py"
    stdout_path = os.path.join(log_dir, "Controller_stdout.txt")
    stderr_path = os.path.join(log_dir, "Controller_stderr.txt")
    with open(stdout_path, "w") as out_file, open(stderr_path, "w") as err_file:
        process = subprocess.Popen(["/usr/bin/python3", script_dir], stdout=out_file, stderr=err_file)
    return process

def start_battery_broadcast():
    global broadcast_enabled

    while broadcast_enabled:
        send_battery_voltage()
        time.sleep(0.25)  # Adjust the sleep duration as needed

    # Additional cleanup or final actions can be added here
    print("Battery broadcast thread stopped.")

def stop_battery_broadcast():
    global broadcast_enabled
    broadcast_enabled = False  # Set the flag to stop the broadcast thread

def restart_battery_broadcast():
    global broadcast_enabled, battery_broadcast_thread

    # Wait for a short duration before restarting the broadcast
    time.sleep(1)

    # Reset the broadcast flag and start the thread again
    broadcast_enabled = True
    battery_broadcast_thread = threading.Thread(target=start_battery_broadcast, daemon=True)
    battery_broadcast_thread.start()

def handle_message(message):
    global process, ser, serial_running, battery_broadcast_thread

    if message == "disable":
        print("Received 'disable' message. Stopping Controller.py")
        if process and process.poll() is None:
            process.terminate()
            process.communicate()  # Wait for the subprocess to complete

        if not serial_running:
            start_serial()

        # Stop the battery broadcast thread
        stop_battery_broadcast()

        # Restart the battery broadcast thread after a short delay
        restart_battery_broadcast()

    elif message == "enable":
        print("Received 'enable' message. Starting Controller.py")
        if serial_running:
            stop_battery_broadcast()
            stop_serial()
            time.sleep(1)  # Delay for 1 second
        
        if not process or process.poll() is not None:
            start_controller()
        else:
            print("Controller.py is already running.")
    else:
        print(f"Received unknown message: {message}")

def cleanup_zombies():
    for proc in psutil.process_iter(['pid', 'name', 'status']):
        if proc.info['status'] == psutil.STATUS_ZOMBIE:
            print(f"Terminating zombie process: {proc.info['name']} ({proc.info['pid']})")
            try:
                psutil.Process(proc.info['pid']).terminate()
            except psutil.NoSuchProcess:
                pass

def start_serial():
    global ser, serial_running
    try:
        ser = serial.Serial(serial_port, baud_rate, timeout=1)
        serial_running = True
        print(f"Serial port {serial_port} opened.")
        time.sleep(1)  # Delay to stabilize the serial connection
    except Exception as e:
        print(f"Error opening serial port: {e}")

def stop_serial():
    global ser, serial_running
    try:
        ser.close()
        serial_running = False
        print(f"Serial port {serial_port} closed.")
    except Exception as e:
        print(f"Error closing serial port: {e}")

def read_battery_voltage():
    global ser
    try:
        if not ser or not ser.is_open:
            start_serial()  # Call start_serial without parameters
        
        data = ser.readline().decode('utf-8').strip()
        if data:
            # Extract the numeric part representing the battery voltage
            voltage_part = data.split('Battery Voltage: ')[-1]
            try:
                battery_voltage = float(voltage_part)
                print(f"Battery Voltage: {battery_voltage}")
                return battery_voltage
            except ValueError as ve:
                print(f"Error converting string to float: {ve}")
                return None
        else:
            print("Empty data received from serial port.")
            return None
    except Exception as e:
        print(f"Error reading battery voltage: {e}")
        return None

def send_battery_voltage():
    battery_voltage = read_battery_voltage()
    if battery_voltage is not None:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as data_socket:
                data_socket.sendto(str(battery_voltage).encode('utf-8'), (client, data_port))
                print(f"Sent battery voltage to {client}:{data_port}: {battery_voltage}")
        except Exception as e:
            print(f"Error sending battery voltage: {e}")


def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, control_port))
    server_socket.listen(1)

    print(f"Server listening on {host}:{control_port}")

    while True:
        cleanup_zombies()
        client_socket, client_address = server_socket.accept()
        print(f"Connection established with {client_address}")

        try:
            data = client_socket.recv(1024).decode('utf-8')
            if data:
                print(f"Received message from client: {data}")
                handle_message(data)
        except Exception as e:
            print(f"Error receiving message: {e}")
        finally:
            client_socket.close()

if __name__ == "__main__":
    # Start battery voltage broadcast in a separate thread
    battery_broadcast_thread = threading.Thread(target=start_battery_broadcast, daemon=True)
    battery_broadcast_thread.start()

    # Start the main server to handle control messages
    start_server()
