import socket, network, utime, machine

def gps_fix(gps_module):
    """
    Description:

    A function to make sure that a gps fix have been received before starting the main program.

    Parameters:

    gps_module          ; UART, takes an UART connection from machine import, a build in library in micropython, uses a ublox neo-6m gps module.

    Returns:

    Bool        ; Returns True if a geographic coordinate set have been received from the ublox module.
    """
    # Sleeps 0,08s otherwise NMEA sentences are not returned in one sentence, 
    # this most likely happens because of the data transfer protocol from the ublox module to the pico.
    utime.sleep(0.08)

    # Array for storing NMEA sentences.
    NMEA_array = bytearray(255)

    # Read the array
    NMEA_array = str(gps_module.readline())

    # Split the message using ','.
    NMEA_sentence = NMEA_array.split(',')

    # Return True if a real geographic coordinate set have been received.
    if NMEA_sentence[0] is "b'$GPGGA":
        if (NMEA_sentence[3] is ('N' or 'S')) and (NMEA_sentence[5] is ('E' or 'W')):
            return True

    # Else return False.
    return False


def get_coordinates(gps_module, gps_read_amount):
    """
    Description:

    A function to extract Latitude and Longitude from a Ublox Neo-6m GPS module.

    Parameters:

    gps_module          ; UART, takes an UART connection from machine import, a build in library in micropython, uses a ublox neo-6m gps module.

    gps_read_amount     ; Int, the amount of collected GPS coordinates that should be used to get an average coordinate set.

    Returns:

    List       ; [float Latitude, float Longitude], returns a list containing the GPS position in Latitude and Longitude.
    """
    # A list for getting the average coordinates
    coordinates_list_lat = []
    coordinates_list_long = []

    # Array for storing NMEA sentences.
    NMEA_array = bytearray(255)

    while True:
        # Sleeps 0,08s otherwise NMEA sentences are not returned in one sentence.
        utime.sleep(0.08)

        # Read the array
        NMEA_array = str(gps_module.readline())

        # Split the message using ','.
        NMEA_sentence = NMEA_array.split(',')
        # Check if it is the right NMEA sentence (the one with coordinates).
        if NMEA_sentence[0] is "b'$GPGGA":
            try:
                if (NMEA_sentence[3] is ('N' or 'S')) and (NMEA_sentence[5] is ('E' or 'W')):
                    latitude = decimal_degree_converter(NMEA_sentence[2], NMEA_sentence[3])
                    longitude = decimal_degree_converter(NMEA_sentence[4], NMEA_sentence[5])

                    coordinates_list_lat.append(latitude)
                    coordinates_list_long.append(longitude)

                    if len(coordinates_list_lat) == gps_read_amount:
                        return [sum(coordinates_list_lat)/len(coordinates_list_lat), sum(coordinates_list_long)/len(coordinates_list_long)]


            except Exception:
                None


def decimal_degree_converter(geographic_coordinate, geographic_indicator):

    """
    Description:

    Converts NMEA coordinates to decimal degrees

    Parameters:

    geographic_coordinate    ; str, one NMEA coordinate as a string.

    georaphic_indicator      ; str, specifies if the coordinate is north N, south S, east E or west W.

    Returns:

    conversion      ; float, the converted NMEA coordinate in decimal degrees.
    """
    # Convert to DDSS.SSSSS latitude
    if geographic_indicator is 'N' or 'E':
        degrees = (int(float(geographic_coordinate)/100))
        seconds = float(geographic_coordinate) - degrees*100

        # If north or east, add seconds.
        conversion = degrees + seconds/60
        return conversion

    elif geographic_indicator is 'S' or 'W':
        degrees = (int(float(geographic_coordinate)/100))
        seconds = float(geographic_coordinate) - degrees*100

        # If south or west, negate seconds.
        conversion = degrees - seconds/60
        return conversion


def wlan_connect_drone_ap(ssid_drone='TELLO-gruppe-153', password_drone='pass=trold32'):
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
    while pico_wlan.isconnected() == False:
        None

    return pico_wlan


def wlan_disconnect_drone_ap(wlan):
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
            utime.sleep(3)
            # Console DEBUG
            # print('sent: command')
            break
        except Exception as error:
            # Console DEBUG
            # print(f'Drone is not connected! ({error})')
            None

    return (server_socket, tello_address)


def server_socket_close(socket):
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


def send_command(command, time_s, server_socket, drone_address):
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
    utime.sleep(time_s)


def pico_access_point_create(ssid_pico="PicoW", password_pico="123456789"):
    """
    Description:

    Creates and enables a wireless access point using the Wi-Fi module onboard the RaspberryPi Pico W, 
    with a configurable name and password.

    Parameters:

    ssid_pico       ; Str, normally "PicoW", the chosen name for the access point.

    password_pico   ; Str, normally "123456789", the chosen password for the access point.

    Returns:

    pico_access_point       ; Var, of the type network.WLAN(network.AP_IF) 

    """
    # Use the LED pin on the RaspberryPi Pico W for debugging purposes.
    LED = machine.Pin('LED', machine.Pin.OUT)

    # Turn on the led to see that the pico was powered on.
    LED.value(1)

    # Create and enable the access point.
    try:
        pico_access_point = network.WLAN(network.AP_IF)
        pico_access_point.config(ssid=ssid_pico, password=password_pico) 
        pico_access_point.active(True)
    except Exception as e:
        # Console DEBUG
        # print(e)
        return
    
    # Turn it off if the pico had enough power to create the access point.
    utime.sleep(1)
    LED.value(0)

    # Console DEBUG
    # print("Access point active")
    # print(pico_access_point.ifconfig())

    # return the network.wlan(network.AP_IF), access point.
    return pico_access_point


def pico_access_point_end(access_point):
    """
    Description:

    Power off an access point generated by the RaspberryPi Pico W.

    Parameters:

    access_point        ; Var of the type network.WLAN(network.AP_IF).
    """
    # Console DEBUG
    # print('Access point closed!')
    access_point.active(False)
    access_point.disconnect()


def pico_data_control(access_point):
    """
    Description:

    Creates a TCP server using the RaspberryPi Pico W, that sends data from 
    the Pico W to the monitor, when receiving a request from the client.

    Parameters:

    access_point        ; Var of the type network.WLAN(network.AP_IF).
    """
    # Create a UART connection between the Pico W and the GPS module, using the rx Pin GP5, 
    # (pin 7 in the datasheet a.k.a. UART1_RX, as it is receiving), on the Pico W 
    # and pin 4 (TX, as it is transmitting) on the Neo-6m GPS module.
    GPS = machine.UART(1, baudrate=9600, tx=machine.Pin(4), rx=machine.Pin(5))

    # Create the TCP server socket.
    server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    
    # Prefered host IP of the RaspberryPi Pico W and a port for the data to stream through.
    host = '192.168.4.1'
    port = 12345

    # Bind the TCP server socket to the host IP and port.
    server_socket.bind((host, port))

    # Listen for a client on the host IP and the chosen port, only enable 1 connection.
    server_socket.listen(1)

    counter = 0

    # Activate the rest of the program, if the gps has a fix.
    while gps_fix(GPS) == False:
        pass

    while True:
        # Accept the client if it connects to the port.
        client, address = server_socket.accept()

        while True:
            # Create a variable for the receiving request message from the client.
            return_data = client.recv(64)

            # If the request message is b'exit', close the server and end the program.
            if str(return_data) is "b'emergency'":

                # send_command('land', 5, server_socket_drone, drone_address_drone)
                pico_access_point_end(access_point)
                client.close()
                print('Emergency land!')
                return

            # The first received message from the monitor
            if 'network' in str(return_data):
                variables_set_list = str(return_data)
                variables_set_list = variables_set_list.split(' ')
                network_ssid = str(variables_set_list[1])
                network_scan_amount = str(variables_set_list[2])
                gps_read_amount = str(variables_set_list[3][0:len(variables_set_list[3])-1])
                
                print(network_ssid, network_scan_amount, gps_read_amount)

            # Scan the network and assign the RSSI value to a variable.
            scan = pico_network_scan(network_ssid, int(network_scan_amount))

            # The RSSI value in the tuple returned by the pico_network_scan() function
            rssi = scan[0]

            # Collect the GPS coordinates, using the module these have already been converted from NMEA to geographic coordinates.
            coordinates = get_coordinates(GPS, int(gps_read_amount))

            # Make a list of the data consisting of [Latitude, Longitude, RSSI].
            data_list = [coordinates[0], coordinates[1], rssi]

            # Convert the data_list into a string and encode it so the server can send the reply in binary.
            data_str = str(data_list)
            encoded_data = data_str.encode()

            # Console DEBUG
            # print(f'Client: {client}, Address: {address}, Data: {encoded_data}.')

            # if the request message had nothing in it break, else send the data as a reply to the client.
            if not return_data:
                break
            else:
                client.sendall(encoded_data)
                counter += 1

                if counter == 1:
                    # send_command('takeoff', 3, server_socket_drone, drone_address_drone)
                    print('1')

                elif counter == 2:
                    #send_command('right 50', 4, server_socket_drone, drone_address_drone)
                    print('2')
                elif counter == 6:
                    #send_command('land', 2, server_socket_drone, drone_address_drone)
                    client.sendall(b'finished')
                    utime.sleep(1)
                    # Stop server
                    pico_access_point_end(access_point)
                    client.close()
                    print('Closed server')
                    return
                    

def pico_network_scan(wifi_ssid, scan_amount = 10, time_between_scans = 0):
    """
    Description:

    Scans a given network, and returns the avg RSSI value and a list with all RSSI values based on a given amount of scans.

    Parameters:

    wifi_ssid           ; Str, the name of the wifi that should be scanned.

    scan_amount         ; Int, the amount of scans to be made on that wifi network.

    time_between_scans  ; Float, the time between each scan besides the time the scan itself takes.
    """
    # Create a list to contain RSSI values.
    RSSI_list = []

    # Create a new STA_IF network interface
    pico_scan_wlan = network.WLAN(network.STA_IF)
    pico_scan_wlan.active(True)

    # Loop until scan_amount enables a return.
    while True:
        # Scan wlan and collect the a RSSI value.
        networks = pico_scan_wlan.scan()

        for network_data in networks:
            if network_data[0].decode() == wifi_ssid:
                # Append the RSSI value to the RSSI list.
                RSSI_list.append(network_data[3])
        
        # Sleep the given amount.
        utime.sleep(time_between_scans)

        # If the scan_amount have been reached return the average RSSI, 
        # the RSSI_list and the name of the wifi that was scanned.
        if len(RSSI_list) >= scan_amount: 
            avg_RSSI = sum(RSSI_list)/len(RSSI_list)
            return [avg_RSSI, RSSI_list, wifi_ssid]


# program:
# wlan = wlan_connect_drone_ap()
# server_socket_address = server_socket_bind()

# server_socket_drone = server_socket_address[0]
# drone_address_drone = server_socket_address[1]

pico_ap = pico_access_point_create()

pico_data_control(pico_ap)

# End connections
# wlan_disconnect_drone_ap(wlan)
# server_socket_close(server_socket_drone)