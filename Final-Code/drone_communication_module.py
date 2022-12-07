import socket, network, time

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
    # Connect to the drone's access point using the wlan STA_IF (station / client) interface.
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
    """
    Description:

    Sends SDK commands to the drone an UDP server connected to the drone's access point.

    Parameters:

    command         ; Str, the action / command you want the drone to perform, see the tello SDK document: https://dl-cdn.ryzerobotics.com/downloads/Tello/Tello%20SDK%202.0%20User%20Guide.pdf

    time_s          ; Float, time to wait before doing continuing, this is done to avoid overlapping commands, when these are performed in succession.

    server_socket   ; Var as socket.socket(socket.AF_INET, socket.SOCK_DGRAM), a UDP server for sending the commands to the drone.

    drone_address   ; Var as (drone_ip, drone_port), normally the ip is '192.168.10.1' and the port is '8889'.
    """

    # Convert the command str to a bytes object.
    command = bytes(command, 'utf-8')
    
    # Send the bytes object to the drone's address through its access point by using the UDP server.
    server_socket.sendto(command, drone_address)
    # Console DEBUG
    # print(f'sent: {command}')
    time.sleep(time_s)
        
# program:
drone_wlan_connect()
server_socket_address = server_socket_bind()

server_socket = server_socket_address[0]
drone_address = server_socket_address[1]

drone_socket_send_command('takeoff', 6, server_socket, drone_address)
drone_socket_send_command('land', 5, server_socket, drone_address)

# End connections
wlan_disconnect(server_socket)
drone_socket_close(server_socket)
