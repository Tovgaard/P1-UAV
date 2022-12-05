import socket, network, time, binascii
global drone_socket
# ssid and password for the drone's access point.
ssid_tello = 'TELLO-gruppe-153'
password_tello = 'pass=trold32'

# ssid and password for raspberry pi Pico W access point.
ssid_pico = "PicoW"
password_pico = "123456789"

# Connect to drone access point via wlan.
def drone_wlan_connect():
    global wlan
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid_tello, password_tello)
    
    if wlan.isconnected() == False:
        print('wlan is not connected!')
        return
        
    ip = wlan.ifconfig()[0]
    print(f'Connected on {ip}')

# Disconnect drone from drone hotspot.
def wlan_disconnect():
    global wlan
    if wlan.isconnected() == True:
        wlan.active(False)
        wlan.disconnect()
        print('wlan disconnected!')
    else:
        print('wlan did not disconnect!')


# Create tello drone socket and bind Raspberrypi Pico W connection to it.
def drone_socket_bind():
    global drone_socket
    # Assign ip and port to client and server
    # Client
    tello_ip = '192.168.10.1'
    tello_port = 8889

    # Server
    local_ip = ''
    local_port = 8889

    # Initialize socket and bind it to the server's ip and port.
    drone_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    drone_socket.bind((local_ip, local_port))

    tello_address = (tello_ip, tello_port)

    # Initialize the Tello drone, by sending "command".
    while True:
        try:
            drone_socket.sendto(b'command', tello_address)
            print('sent: command')
            break
        except Exception as error:
            print(f'Drone is not connected! ({error})')


def drone_socket_close():
    global drone_socket
    drone_socket.close()
    print('Socket closed!')

def drone_socket_send_command(command, time_s):

    tello_ip = '192.168.10.1'
    tello_port = 8889
    tello_address = (tello_ip, tello_port)

    command = bytes(command, 'utf-8')
    
    drone_socket.sendto(command, tello_address)
    print(f'sent: {command}')
    time.sleep(time_s)
        

# Create an access point on Raspberry Pico W, for a computer to connect to.
def pico_access_point_create():
    global pico_access_point
    pico_access_point = network.WLAN(network.AP_IF)
    pico_access_point.config(essid=ssid_pico, password=password_pico) 
    pico_access_point.active(True)

    while pico_access_point.active == False:
        pass

    print("Access point active")
    print(pico_access_point.ifconfig())

def pico_access_point_end():
    pico_access_point.active(False)
    time.sleep(1)
    print('Access point closed!')


def network_scan(scan_amount = 60, wifi_name = 'OnePlus 9 Pro', time_between_network_scans = 0.1):
    channel_received = False
    wifi_avg_list = []
    channel = []

    wlan = network.WLAN()
    wlan.active(True)

    while channel_received == False:
        networks = wlan.scan()
        for w in networks:
            if w[0].decode() == wifi_name:
                channel.append(w[2])
                channel_received = True
                print(f'Access point {wifi_name} found!')

    while True:
        networks = wlan.scan()

        for w in networks:
            if w[0].decode() == wifi_name:
                wifi_avg_list.append(w[3])
                channel.append(w[2])
        
        time.sleep(time_between_network_scans)

        if len(wifi_avg_list) >= scan_amount: 
            avg_dBm = sum(wifi_avg_list)/len(wifi_avg_list)
            return [channel, avg_dBm, wifi_avg_list, wifi_name]


# program:
try:
    wlan_disconnect()
except Exception as e:
    print(f'wlan did not disconnect! ({e})')

drone_wlan_connect()
drone_socket_bind()

drone_socket_send_command('takeoff', 6)
drone_socket_send_command('land', 5)

# Commands: https://dl-cdn.ryzerobotics.com/downloads/Tello/Tello%20SDK%202.0%20User%20Guide.pdf

# End connections
wlan_disconnect()
drone_socket_close()
