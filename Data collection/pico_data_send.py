# Micropython, runs on the raspberry pi Pico W
import network, socket, random, machine, utime

def pico_access_point_create(ssid_pico="PicoW", password_pico="123456789"):
    LED = machine.Pin('LED', machine.Pin.OUT)

    LED.value(1)
    try:
        pico_access_point = network.WLAN(network.AP_IF)
        pico_access_point.config(ssid=ssid_pico, password=password_pico) 
        pico_access_point.active(True)
    except Exception as e:
        print(e)
    utime.sleep(1)
    LED.value(0)

    print("Access point active")
    print(pico_access_point.ifconfig())

    return pico_access_point

def pico_access_point_end(access_point):
    access_point.active(False)
    access_point.disconnect()
    print('Access point closed!')

def pico_data_send(access_point):
    # Server socket: Pico W
    server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    
    host = '192.168.4.1' #ip of raspberry pi
    port = 12345

    server_socket.bind((host, port))
    server_socket.listen(1)

    LED = machine.Pin('LED', machine.Pin.OUT)

    while True:

        client, address = server_socket.accept()

        try:
            while True:
                
                LED.value(1)

                return_data = client.recv(64)

                # if recv data is b'exit', close the server and end the program
                if str(return_data) is "b'exit'":
                    print('Exit received, closing server!')
                    pico_access_point_end(hotspot)
                    client.close()
                    return
                
                # [Lat, Long, RSSI]
                data = [random.randint(1, 25), random.randint(1, 25), random.randint(1, 25)]

                # Encode the data
                data_str = str(data)
                encoded_data = data_str.encode()

                print(f'Client: {client}, Address: {address}, Data: {encoded_data}.')

                utime.sleep(0.5)
                LED.value(0)
                utime.sleep(0.5)
                
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

#pico_access_point_end(hotspot)