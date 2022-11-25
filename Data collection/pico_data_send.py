# Micropython, runs on the raspberry pi Pico W
import network, socket

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
    server_socket = socket.socket()

    host = '192.168.4.1' #ip of raspberry pi
    port = 12345

    server_socket.bind((host, port))
    server_socket.listen()

    data_packet = str(data)
    data_packet = data_packet.encode()

    while True:
        client, addr = server_socket.accept()
        client.send(data_packet)
        client.close()


pico_access_point_create(ssid_pico, password_pico)

pico_data_send([12, 32, -65])

#pico_access_point_end()

