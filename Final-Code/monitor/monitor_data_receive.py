import socket, time  

# Client socket: monitor.

# Dummy data packet variable

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  

host = '192.168.4.1'    # ip of raspberry pi pico W
port = 12345

client_socket.connect((host, port))

length = 0

client_counter = 0

while True:

    if client_counter == 2:
        client_socket.sendall(b'exit') # Close the server on the pico, after we're done
        client_socket.close()
        print('Send closing message to server!')
        break

    client_socket.sendall(b'Send data!')
    received_data_packet = client_socket.recv(64)
    decoded_data = received_data_packet.decode('utf-8')

    client_counter += 1

    try:
        eval_data = eval(decoded_data)
        print(f'Data: {eval_data}, type: {type(eval_data)}')
    except Exception as a:
        print(a)
    
    client_socket.sendall(b'next')

    time.sleep(1)

