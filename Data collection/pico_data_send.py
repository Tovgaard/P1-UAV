# Micropython, runs on the raspberry pi Pico W
import network, socket, random, time

def pico_access_point_create(ssid_pico="PicoW", password_pico="123456789"):

    pico_access_point = network.WLAN(network.AP_IF)
    pico_access_point.config(ssid=ssid_pico, password=password_pico) 
    pico_access_point.active(True)

    while pico_access_point.active == False:
        None

    print("Access point active")
    print(pico_access_point.ifconfig())

    return pico_access_point

def pico_access_point_end(access_point):
    access_point.active(False)
    print('Access point closed!')

def pico_data_send(access_point):
    # Server socket: Pico W
    server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    
    host = '192.168.4.1' #ip of raspberry pi
    port = 12345

    server_socket.bind((host, port))
    server_socket.listen(1)

    while True:

        client, address = server_socket.accept()

        try:
            while True:
                return_data = client.recv(64)
                
                # [Lat, Long, RSSI]
                data = [random.randint(1, 25), random.randint(1, 25), random.randint(1, 25)]

                # Encode the data
                data_str = str(data)
                encoded_data = data_str.encode()

                print(f'Client: {client}, Address: {address}, Data: {encoded_data}.')

                if not return_data:
                    break

                client.sendall(encoded_data) 

        except KeyboardInterrupt as a:
            print(a)
            pico_access_point_end(access_point)
            client.close()
        except OSError as a:
            print(a)
            pico_access_point_end(access_point)
            client.close()

hotspot = pico_access_point_create()
pico_data_send(hotspot)

#pico_access_point_end()