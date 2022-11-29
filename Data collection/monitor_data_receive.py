import socket, time  

# Client socket: monitor

# Dummy data packet variable

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  

host = '192.168.4.1'    # ip of raspberry pi 
port = 12345

client_socket.connect((host, port))

length = 0

while True:
    client_socket.sendall(b'Ready for data!')
    received_data_packet = client_socket.recv(64)
    decoded_data = received_data_packet.decode('utf-8')

    length += 1

    try:
        eval_data = eval(decoded_data)
        print(f'Data: {eval_data}, type: {type(eval_data)}')
    except Exception as a:
        print(a)
      
    if length >= 5:
        client_socket.close()
        break

    time.sleep(1.5)

