import socket, network, time, binascii

# ssid and password for the drone's access point.
ssid_tello = 'TELLO-gruppe-153'
password_tello = 'pass=trold32'

# ssid and password for raspberry pi Pico W access point.
ssid_pico = "PicoW"
password_pico = "123456789"

# Connect to drone access point via wlan.
def wlan_connect():
    global wlan
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid_tello, password_tello)
    
    while wlan.isconnected() == False:
            print('wlan is not connected!')
            return
        
    ip = wlan.ifconfig()[0]
    print(f'Connected on {ip}')

# Disconnect drone from drone hotspot.
def wlan_disconnect():
    if wlan.isconnected() == True:
        wlan.disconnect
        if wlan.isconnected() == True:
            print('wlan disconnected!')
        else:
            print('wlan did not disconnect!')
    else:
        print('wlan not active')

# Create tello drone socket and bind Raspberrypi Pico W connection to it.
def drone_socket_bind():
    global socket
    # Assign ip and port to client and server
    # Client
    tello_ip = '192.168.10.1'
    tello_port = 8889

    # Server
    local_ip = ''
    local_port = 8889

    # Initialize socket and bind it to the server's ip and port.
    socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    socket.bind((local_ip, local_port))

    tello_address = (tello_ip, tello_port)

    # Initialize the Tello drone, by sending "command".
    try:
        socket.sendto(b'command', tello_address)
        print('sent: command')
    except:
        print('Drone is not connected!')

def drone_socket_close():
    socket.close
    print('Socket closed!')

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

def network_scan():
    wlan = network.WLAN() #  network.WLAN(network.STA_IF)
    wlan.active(True)
    networks = wlan.scan() # list with tupples with 6 fields ssid, bssid, channel, RSSI, security, hidden
    i=0

    networks.sort(key=lambda x:x[3],reverse=True) # sorted on RSSI (3)
    for w in networks:
        i+=1
        print(i,w[0].decode(),binascii.hexlify(w[1]).decode(),w[2],w[3],w[4],w[5])


network_scan()

# program:
pico_access_point_create()
wlan_connect()
drone_socket_bind()


# End connections
wlan_disconnect()
drone_socket_close()
pico_access_point_end()




