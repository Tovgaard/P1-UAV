# Micropython, runs on the raspberry pi Pico W
import network, socket, random, time

# ssid and password for raspberry pi Pico W access point.
ssid_pico = "PicoW"
password_pico = "123456789"

def pico_access_point_create(ssid_pico, password_pico):
    global pico_access_point
    pico_access_point = network.WLAN(network.AP_IF)
    pico_access_point.config(ssid=ssid_pico, password=password_pico) 
    pico_access_point.active(True)

    while pico_access_point.active == False:
        print('ja')

    print("Access point active")
    print(pico_access_point.ifconfig())


def pico_access_point_end():
    pico_access_point.active(False)
    print('Access point closed!')

def pico_data_send(data):
    # Server socket: Pico W
    server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    
    host = '192.168.4.1' #ip of raspberry pi
    port = 12345

    server_socket.bind((host, port))
    server_socket.listen(1)

    data_packet = str(data)
    data_packet = data_packet.encode()

    try:
        client, addr = server_socket.accept()
        print(f'Client: {client}, Address: {addr}')
        client.sendall(data_packet)
        client.close()
    except KeyboardInterrupt:
        pico_access_point_end()
    except OSError:
        pico_access_point_end()
            
pico_access_point_create(ssid_pico, password_pico)

while True:
    s = random.randint(1, 25)
    try:
        pico_data_send(s)
        print(f'Data send! {s}')
        #print(pico_access_point.scan())
    except OSError as e:
        None