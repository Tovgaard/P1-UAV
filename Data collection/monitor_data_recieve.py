import socket               


# Client socket: monitor

# Dummy data packet variable

client_socket = socket.socket()        
host = '192.168.4.1'# ip of raspberry pi 
port = 12345  

try:             
    client_socket .connect((host, port))
    received_data_packet = client_socket.recv(1024)
    client_socket .close()
except Exception:
    print('No connection could be established')

try:
    decoded_data = eval(received_data_packet.decode('utf-8'))
except Exception:
    print('Packet not decoded correctly, try again')


print(decoded_data)

