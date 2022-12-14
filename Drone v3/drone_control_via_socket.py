import socket, time

# Assign ip and port to client and server
# Client
tello_ip = '192.168.10.1'
tello_port = 8889

# Server
local_ip = '0.0.0.0'
local_port = 8890

# Initialize socket and bind it to the server's ip and port.
socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
socket.bind((local_ip, local_port))

tello_address = (tello_ip, tello_port)

try:
    # Initialize the Tello drone.
    socket.sendto(b'command', tello_address)
    print('sent: command')
except Exception as i:
    print(i)

# Give the wifi a ssid (service set identifier) and a password.
# socket.sendto(b'wifi gruppe-153 pass=trold32', tello_address)

# Send command 'takeoff' to Tello drone
socket.sendto(b'takeoff', tello_address)
print('sent: takeoff')
time.sleep(5)

while True:
    # Send command 'land' to Tello drone
    socket.sendto(b'land', tello_address)
    print('sent: landing')
    time.sleep(2)

# Close socket connection to prevent the server from listing for the client indefinitely.
socket.close
print('Closed connection!')