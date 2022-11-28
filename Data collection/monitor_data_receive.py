import socket, time  

# Client socket: monitor

# Dummy data packet variable

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  

host = '192.168.4.1'    # ip of raspberry pi 
port = 12345

number = 0

client_socket.connect((host, port))

while True:
    if number == 5:
        client_socket.close()
        break
    else:
        received_data_packet = client_socket.recv(4096).decode('utf-8')
        print(received_data_packet)
        try:
            decoded_data = eval(received_data_packet)
        except Exception:
            None

        print(decoded_data)
        time.sleep(1.5)
        number += 1

