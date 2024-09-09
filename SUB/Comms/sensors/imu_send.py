'''
imu_send.py

Intakes imu output and streams to control over port 5610

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
2023/01/04 CEH Initial Version


####################################################################################
'''
#!/usr/bin/python
import socket
import smbus2 as smbus			#import SMBus module of I2C
import struct
import time

#some MPU6050 Registers and their Address
PWR_MGMT_1   = 0x6B
SMPLRT_DIV   = 0x19
CONFIG       = 0x1A
GYRO_CONFIG  = 0x1B
INT_ENABLE   = 0x38
ACCEL_XOUT_H = 0x3B
ACCEL_YOUT_H = 0x3D
ACCEL_ZOUT_H = 0x3F
GYRO_XOUT_H  = 0x43
GYRO_YOUT_H  = 0x45
GYRO_ZOUT_H  = 0x47


def MPU_Init():
	#write to sample rate register
	bus.write_byte_data(Device_Address, SMPLRT_DIV, 7)

	#Write to power management register
	bus.write_byte_data(Device_Address, PWR_MGMT_1, 1)

	#Write to Configuration register
	bus.write_byte_data(Device_Address, CONFIG, 0)

	#Write to Gyro configuration register
	bus.write_byte_data(Device_Address, GYRO_CONFIG, 24)

	#Write to interrupt enable register
	bus.write_byte_data(Device_Address, INT_ENABLE, 1)

def read_raw_data(addr):
	#Accelero and Gyro value are 16-bit
        high = bus.read_byte_data(Device_Address, addr)
        low = bus.read_byte_data(Device_Address, addr+1)

        #concatenate higher and lower value
        value = ((high << 8) | low)

        #to get signed value from mpu6050
        if(value > 32768):
                value = value - 65536
        return value


bus = smbus.SMBus(1) 	# or bus = smbus.SMBus(0) for older version boards
Device_Address = 0x68   # MPU6050 device address

MPU_Init()

print (" Reading Data of Gyroscope and Accelerometer")

time.sleep(1)

def main():
	server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server_socket.bind(("192.168.2.3",5610))  # Change the port as needed
	server_socket.listen()

	print("TCP server sending imu on port 5610")
	try:
		while True:
			client_socket, _ = server_socket.accept()
			while True:
				#Read Accelerometer raw value
				acc_x = read_raw_data(ACCEL_XOUT_H)
				acc_y = read_raw_data(ACCEL_YOUT_H)
				acc_z = read_raw_data(ACCEL_ZOUT_H)

				#Read Gyroscope raw value
				gyro_x = read_raw_data(GYRO_XOUT_H)
				gyro_y = read_raw_data(GYRO_YOUT_H)
				gyro_z = read_raw_data(GYRO_ZOUT_H)

				#Full scale range +/- 250 degree/C as per sensitivity scale factor
				Ax = acc_x/16384.0
				Ay = acc_y/16384.0
				Az = acc_z/16384.0

				Gx = gyro_x/131.0
				Gy = gyro_y/131.0
				Gz = gyro_z/131.0

				#message = "Gx=%.2f %s Gy=%.2f %s Gz=%.2f %s Ax=%.2f g\t Ay=%.2f g\t Az=%.2f g\n" % (Gx, u'\u00b0' + "/s ", Gy, u'\u00b0' + "/s ", Gz, u'\u00b0' + "/s ", Ax, Ay, Az)

				data = struct.pack('ffffff', Gx, Gy, Gz, Ax, Ay, Az)

				client_socket.sendall(data)
				time.sleep(1)

		client_socket.close()

	except Exception as e:
		print(f"Error: {e}")
	finally:
		server_socket.close()

if __name__ == "__main__":
    main()