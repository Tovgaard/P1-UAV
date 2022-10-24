import socket
import time

# Assign ip and port to client and host
tello_ip = '192.168.10.1'
tello_port = 8889

# '', 8889
local_ip = '0.0.0.0'
local_port = 8890

# Initialize socket and bind it to host
socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
socket.bind((local_ip, local_port))

tello_address = (tello_ip, tello_port)

# Initialize Tello SDK
socket.sendto(b'command', tello_address)
print('sent: command')

# Send command 'takeoff' to Tello drone
socket.sendto(b'takeoff', tello_address)
print('sent: takeoff')
time.sleep(10)

# Send command 'land' to Tello drone
socket.sendto(b'land', tello_address)
print('sent: landing')

# Close socket connection to prevent indefinite listing
socket.close
print('Closed connection!')