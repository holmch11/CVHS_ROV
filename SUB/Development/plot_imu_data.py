'''
plot_imu_data.py

This collects imu data and creates realtime 1 minute rolling plot on CVHS SUB

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
import time
import smbus2 as smbus
import matplotlib.pyplot as plt
from flask import Flask, render_template
from io import BytesIO
from flask_sockets import Sockets
import threading
import base64

app = Flask(__name__)
sockets = Sockets(app)

plot_data = ""

# some MPU6050 Registers and their Address
PWR_MGMT_1 = 0x6B
SMPLRT_DIV = 0x19
CONFIG = 0x1A
GYRO_CONFIG = 0x1B
INT_ENABLE = 0x38
ACCEL_XOUT_H = 0x3B
ACCEL_YOUT_H = 0x3D
ACCEL_ZOUT_H = 0x3F
GYRO_XOUT_H = 0x43
GYRO_YOUT_H = 0x45
GYRO_ZOUT_H = 0x47

bus = smbus.SMBus(1)  # or bus = smbus.SMBus(0) for older version boards
Device_Address = 0x68  # MPU6050 device address

num_readings = 30  # number of readings to display on the plot

# Lists to store time and sensor data
timestamps = []
Ax_data = []
Ay_data = []
Az_data = []
Gx_data = []
Gy_data = []
Gz_data = []

plt.style.use('dark_background')

fig_table, ax_table = plt.subplots()
ax_table.axis('off')  # Hide the axes

# Initialize the table with headers
table_data = [['Timestamp', 'Ax', 'Ay', 'Az', 'Gx', 'Gy', 'Gz']]
table = ax_table.table(cellText=table_data, loc='center', colWidths=[0.15] * 7)


def MPU_Init():
    # write to sample rate register
    bus.write_byte_data(Device_Address, SMPLRT_DIV, 7)

    # Write to power management register
    bus.write_byte_data(Device_Address, PWR_MGMT_1, 1)

    # Write to Configuration register
    bus.write_byte_data(Device_Address, CONFIG, 0)

    # Write to Gyro configuration register
    bus.write_byte_data(Device_Address, GYRO_CONFIG, 24)

    # Write to interrupt enable register
    bus.write_byte_data(Device_Address, INT_ENABLE, 1)


def read_raw_data(addr):
    # Accelero and Gyro value are 16-bit
    high = bus.read_byte_data(Device_Address, addr)
    low = bus.read_byte_data(Device_Address, addr + 1)

    # concatenate higher and lower value
    value = ((high << 8) | low)

    # to get signed value from mpu6050
    if value > 32768:
        value = value - 65536
    return value


MPU_Init()


@sockets.route('/echo')
def echo_socket(ws):
    while not ws.closed:
        message = ws.receive()
        if message:
            ws.send(message)


def generate_plot():
    while True:
        global timestamps, Ax_data, Ay_data, Az_data, Gx_data, Gy_data, Gz_data

        # Read Accelerometer raw value
        acc_x = read_raw_data(ACCEL_XOUT_H)
        acc_y = read_raw_data(ACCEL_YOUT_H)
        acc_z = read_raw_data(ACCEL_ZOUT_H)

        # Read Gyroscope raw value
        gyro_x = read_raw_data(GYRO_XOUT_H)
        gyro_y = read_raw_data(GYRO_YOUT_H)
        gyro_z = read_raw_data(GYRO_ZOUT_H)

        # Full scale range +/- 250 degree/C as per sensitivity scale factor
        Ax = acc_x / 16384.0
        Ay = acc_y / 16384.0
        Az = acc_z / 16384.0
        Gx = gyro_x / 131.0
        Gy = gyro_y / 131.0
        Gz = gyro_z / 131.0
        current_time = time.time()

        # Record Data to list
        timestamps.append(current_time)
        Ax_data.append(Ax)
        Ay_data.append(Ay)
        Az_data.append(Az)
        Gx_data.append(Gx)
        Gy_data.append(Gy)
        Gz_data.append(Gz)
        # Remove old data keeping only the last num_readings data points
        timestamps = timestamps[-num_readings:]
        Ax_data = Ax_data[-num_readings:]
        Ay_data = Ay_data[-num_readings:]
        Az_data = Az_data[-num_readings:]
        Gx_data = Gx_data[-num_readings:]
        Gy_data = Gy_data[-num_readings:]
        Gz_data = Gz_data[-num_readings:]

        plt.plot(timestamps, Ax_data, marker='o', color='blue', label='Ax')
        plt.scatter(timestamps, Ax_data, marker='o', color='blue')
        plt.plot(timestamps, Ay_data, marker='*', color='white', label='Ay')
        plt.scatter(timestamps, Ay_data, marker='*', color='white')
        plt.plot(timestamps, Az_data, marker='>', color='red', label='Az')
        plt.scatter(timestamps, Az_data, marker='>', color='red')
        plt.plot(timestamps, Gx_data, marker=(5, 0), color='green', label='Gx')
        plt.scatter(timestamps, Gx_data, marker=(5, 0), color='green')
        plt.plot(timestamps, Gy_data, marker=(5, 1), color='orange', label='Gy')
        plt.scatter(timestamps, Gy_data, marker=(5, 1), color='orange')
        plt.plot(timestamps, Gz_data, marker='s', color='yellow', label='Gz')
        plt.scatter(timestamps, Gz_data, marker='s', color='yellow')

        plt.xlabel('Time (s)', color='white')
        plt.ylabel('Acceleration (g) or Gyro (deg/sec)', color='white')
        plt.legend(loc=0)
        plt.title('Real-Time IMU Data (Last 30 sec)', color='white')

        # Update the table data
        table_data.append(
            [timestamps[-1], Ax_data[-1], Ay_data[-1], Az_data[-1], Gx_data[-1], Gy_data[-1], Gz_data[-1]])
        table.auto_set_column_width([0, 1, 2, 3, 4, 5, 6])
        table.auto_set_font_size(False)
        table.set_fontsize(8)
        table.scale(1, 1.5)  # Adjust the scaling factor to fit the table

        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)

        global plot_data
        plot_data = base64.b64encode(buffer.read()).decode('utf-8')

        plt.clf()

        time.sleep(1)


@app.route('/')
def index():
    return render_template('index_realtime.html')


@sockets.route('/ws')
def handle_websocket(ws):
    while not ws.closed:
        message = ws.receive()
        if message:
            ws.send(message)


@sockets.route('/plot_data')
def handle_plot_data_socket(ws):
    while not ws.closed:
        # Send Real-Time plot data to the client
        ws.send(plot_data)


if __name__ == '__main__':
    # Start a separate thread for generating real-time data
    thread = threading.Thread(target=generate_plot)
    thread.daemon = True
    thread.start()

    from gevent import pywsgi
    from geventwebsocket.handler import WebSocketHandler

    server = pywsgi.WSGIServer(('127.0.0.1', 5000), app, handler_class=WebSocketHandler)
    server.serve_forever()
