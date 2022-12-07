import socket, network, time

# ssid and password for raspberry pi Pico W access point.
ssid_pico = "PicoW"
password_pico = "123456789"

def drone_wlan_connect(ssid_drone='TELLO-gruppe-153', password_drone='pass=trold32'):
    """
    Description:

    Connect the microcontroller via wlan to the drone's accesspoint.

    Parameters:

    ssid_drone      ; Str, normally 'TELLO-gruppe-153', the ssid of the drone's access point.

    password_drone  ; Str, normally 'pass=trold32', the password of the drone's access point.

    Returns:

    pico_wlan       ; Var as network.WLAN(network.STA_IF), the wlan connection to the drone's access point.
    """
    # Connect to the drone's access point using wlan and STA_IF (station / client).
    pico_wlan = network.WLAN(network.STA_IF)
    pico_wlan.active(True)
    pico_wlan.connect(ssid_drone, password_drone)
    
    # If wlan is not connected return.
    if pico_wlan.isconnected() == False:
        # print('wlan is not connected!')
        return

    return pico_wlan


def wlan_disconnect(wlan):
    """
    Description:

    Disconnect the microcontroller from the drone's access point.

    Parameters:

    wlan        ; Var as network.WLAN(network.STA_IF), the micro controller network connected to the drone's access point.
    """
    # If the wlan connection is still active sever the connection.
    if wlan.isconnected() == True:
        wlan.active(False)
        wlan.disconnect()
        # Console DEBUG
        # print('wlan disconnected!')
    else:
        # Console DEBUG
        # print('wlan did not disconnect!')
        return


def server_socket_bind():
    """ 
    Description:

    Binds the socket to the drone's access point and send an initialization command.

    Returns:

    server_socket       ; Var as socket.socket(socket.AF_INET, socket.SOCK_DGRAM), the UDP server.
    """
    # Assign host ip and port to the client (the drone).
    tello_ip = '192.168.10.1'
    tello_port = 8889

    # Create an UDP server on the microcontroller (Pico W), using the local host.
    local_host = ''
    local_port = 8889

    # Initialize socket and bind it to the server's host ip and port.
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((local_host, local_port))

    # Set the tello address.
    tello_address = (tello_ip, tello_port)

    while True:
        try:
            # Initialize the Tello drone, by sending "command".
            server_socket.sendto(b'command', tello_address)
            # Console DEBUG
            # print('sent: command')
            break
        except Exception as error:
            # Console DEBUG
            # print(f'Drone is not connected! ({error})')
            None

    return (server_socket, tello_address)


def drone_socket_close(socket):
    """
    Description:

    Closes the microcontroller UDP server socket and severs the connection to the drone.

    Parameters:

    socket      ; Var as socket.socket(socket.AF_INET, socket.SOCK_DGRAM), the server socket.
    """
    # Console DEBUG
    # print('Socket closed!')

    # Close the socket.
    socket.close()


def drone_socket_send_command(command, time_s, server_socket, drone_address):

    command = bytes(command, 'utf-8')
    
    server_socket.sendto(command, drone_address)
    print(f'sent: {command}')
    time.sleep(time_s)
        

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
drone_wlan_connect()
server_socket_address = server_socket_bind()

server_socket = server_socket_address[0]
drone_address = server_socket_address[1]

drone_socket_send_command('takeoff', 6, server_socket, drone_address)
drone_socket_send_command('land', 5, server_socket, drone_address)

# SDK commands: https://dl-cdn.ryzerobotics.com/downloads/Tello/Tello%20SDK%202.0%20User%20Guide.pdf

# End connections
wlan_disconnect(server_socket)
drone_socket_close(server_socket)