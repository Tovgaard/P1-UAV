import socket, network, utime, machine, random

# Create functions

def gps_fix(gps_module):
    """
    Description:

    A function to make sure that a gps fix have been received before starting the main program.

    Parameters:

    gps_module          ; UART, takes an UART connection from machine import, a build in library in micropython, uses a ublox neo-6m gps module.

    Returns:

    Bool        ; Returns True if a geographic coordinate set have been received from the ublox module, else False.
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

    List       ; [float Latitude, float Longitude], containing the average GPS position in Latitude and Longitude based on the gps_read_amount.
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
        # Check if it is the correct NMEA sentence (the one with coordinates).
        if NMEA_sentence[0] is "b'$GPGGA":
            try:
                # Check if the NMEA sentence is complete.
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
    
    # Wait for the wlan to connect
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
    else:
        return


def server_socket_bind():
    """ 
    Description:

    Binds the UDP server socket to the local host and sends an initialization command to the drone's socket.

    Returns:

    tuple       ; Consisting of 1. UDP_server_socket as socket.socket(socket.AF_INET, socket.SOCK_DGRAM), 
                  2. tello_socket_address as (IP=192.168.10.1, port=8889), only the port is changable.
    """
    # Assign host ip and port to the client (the drone).
    tello_ip = '192.168.10.1'
    tello_port = 8889

    # Create an UDP server on the microcontroller (Pico W), using the local host.
    local_host = ''
    local_port = 8889

    # Initialize socket and bind it to the server's host ip and port.
    UDP_server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    UDP_server_socket.bind((local_host, local_port))

    # Set the tello address.
    tello_socket_address = (tello_ip, tello_port)

    while True:
        try:
            # Initialize the Tello drone, by sending "command".
            UDP_server_socket.sendto(b'command', tello_socket_address)
            utime.sleep(3)
            break

        except Exception as error:
            None

    return (UDP_server_socket, tello_socket_address)


def send_command(command, time_s, server_socket, drone_socket_address):
    """
    Description:

    Sends SDK commands to the drone an UDP server socket connected to the drone's access point.

    Parameters:

    command         ; Str, the action / command you want the drone to perform, see the tello SDK document: https://dl-cdn.ryzerobotics.com/downloads/Tello/Tello%20SDK%202.0%20User%20Guide.pdf

    time_s          ; Float, time to wait before doing continuing, this is done to avoid overlapping commands, when these are performed in succession.

    server_socket   ; Var as socket.socket(socket.AF_INET, socket.SOCK_DGRAM), a UDP server socket for sending the commands to the drone.

    drone_socket_address   ; Var as (drone_ip, drone_port), normally the ip is '192.168.10.1' and the port is '8889'.
    """

    # Convert the command str to a bytes object.
    command = bytes(command, 'utf-8')
    
    # Send the bytes object to the drone's address through its access point by using the UDP server.
    server_socket.sendto(command, drone_socket_address)

    utime.sleep(time_s)


def pico_access_point_create(LED, ssid_pico="PicoW", password_pico="123456789"):
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
    # Turn on the led to see that the pico was powered on.
    LED.value(1)

    # Create and enable the access point.
    try:
        pico_access_point = network.WLAN(network.AP_IF)
        pico_access_point.config(ssid=ssid_pico, password=password_pico) 
        pico_access_point.active(True)
    except Exception as e:
        return
    
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


def pico_data_control(LED, access_point, UDP_server_socket, drone_socket_address):
    """
    Description:

    Creates a TCP server using the RaspberryPi Pico W, that sends data from 
    the Pico W to the monitor, when receiving a request from the client.

    Parameters:

    LED                 ; Var of the type machine.Pin('LED', machine.Pin.OUT), part of the micropython library.

    access_point        ; Var of the type network.WLAN(network.AP_IF).

    UDP_server_socket   ; Var of the type socket.socket(socket.AF_INET, socket.SOCK_DGRAM).

    drone_socket_address        ; Socket of the Ryze Tello (IP = 192.168.10.1, port = 8889), only the port number is changable.
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

    index_counter = 0

    rssi_list = []
    direction_list = []
    fix = False

    network_ssid = ''
    network_scan_amount = None
    gps_read_amount = None

    # Activate the rest of the program, if the gps has a fix.
    
    while fix == False:
        fix = gps_fix(GPS)
    
    # Turn off the LED to show that the GPS got a fix.
    LED.value(0)

    while True:
        # Turn off the LED.
        LED.value(0)

        # Accept the client if it connects to the port.
        client, address = server_socket.accept()

        while True:
            # Create a variable for the receiving request message from the pico W TCP server.
            return_data = client.recv(64)

            # if the request message had nothing in it break, else send the data as a reply to the client.
            if not return_data:
                break

            # The first received message from the monitor, should always be config, setting up some important variables.
            if 'config' in str(return_data):
                variables_set_list = str(return_data)
                variables_set_list = variables_set_list.split(' ')
                network_ssid = str(variables_set_list[1])
                network_scan_amount = str(variables_set_list[2])
                gps_read_amount = str(variables_set_list[3][0:len(variables_set_list[3])-1])

            # Scan the network and assign the RSSI value to a variable.
            scan = pico_network_scan(UDP_server_socket, drone_socket_address, network_ssid, int(network_scan_amount))

            # Turn off the LED, to show that data is being collected.
            LED.value(0)

            # The RSSI value in the tuple returned by the pico_network_scan() function.
            rssi = scan[0]
            rssi_list.append(rssi)

            # Collect the GPS coordinates, using the module these have already been converted from NMEA to geographic coordinates.
            coordinates = get_coordinates(GPS, int(gps_read_amount))
            
            # Get the new direction the drone needs to head, based on the current and previous RSSI.
            # Only executed once, to start the algorithm.
            if index_counter == 0:
                send_command('takeoff', 5, UDP_server_socket, drone_socket_address)
                new_drone_direction = locating_algorithm(rssi_list[index_counter], rssi_list[index_counter], None, UDP_server_socket, drone_socket_address)
                direction_list.append(new_drone_direction)
            else:
                new_drone_direction = locating_algorithm(rssi_list[index_counter], rssi_list[index_counter-1], direction_list[index_counter-1], UDP_server_socket, drone_socket_address)
                direction_list.append(new_drone_direction)

            # Make a list of the data consisting of [Index_counter, Latitude, Longitude, RSSI, new_drone_direction].
            data_list = [index_counter, coordinates[0], coordinates[1], rssi, new_drone_direction]

            # Convert the data_list into a string and encode it so the server can send the reply in binary.
            data_str = str(data_list)
            encoded_data = data_str.encode()

            # Send it to the monitor
            client.sendall(encoded_data)
            index_counter += 1

            # Visual indicator showing that the server client send data to the monitor.
            LED.value(1)

            # Hardcoded to stop after 30 scans
            if index_counter == 30:
                send_command('land', 5, UDP_server_socket, drone_socket_address)
                client.sendall(b'finished')

                # Turn off the LED and sleep a bit to make sure the final message was send,
                # before ending the access point and closing the socket.
                LED.value(0)
                utime.sleep(1)
                pico_access_point_end(access_point)
                client.close()
                return
                    

def pico_network_scan(UDP_server_socket, drone_socket_address, wifi_ssid, scan_amount = 10, time_between_scans = 0):
    """
    Description:

    Scans a given network, and returns the avg RSSI value and a list with all RSSI values based on a given amount of scans.

    Parameters:

    UDP_server_socket   ; Var of the type socket.socket(socket.AF_INET, socket.SOCK_DGRAM).

    drone_socket_address        ; Socket of the Ryze Tello (IP = 192.168.10.1, port = 8889), only the port number is changable.

    wifi_ssid           ; Str, the name of the wifi that should be scanned.

    scan_amount         ; Int, the amount of scans to be made on that wifi network.

    time_between_scans  ; Float, the time between each scan besides the time the scan itself takes.

    Returns:

    List        ; [avg_RSSI, RSSI_list, wifi_ssid], where avg_RSSI is the average rssi based on scan_amount, 
                  RSSI_list is all RSSI values found during the scan and wifi_ssid is the ssid of the wifi.
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

        # Send dummy command to keep the drone from automatically landing.
        send_command('sdk?', 0, UDP_server_socket, drone_socket_address)


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


def locating_algorithm(current_rssi, previous_rssi, previous_direction, UDP_server_socket, drone_socket_address):
    """
    Description:

    Chooses a new direction based on the the current RSSI scan, previous RSSI scan and the previous direction the drone flew in.

    Parameters:

    current_rssi        ; Float, negative 8 bit number ranging from 0 to -255.

    previous_rssi       ; Float, negative 8 bit number ranging from 0 to -255.

    previous_direction  ; Str, only 'right', 'left', 'forward', 'back'.

    UDP_server_socket   ; Var of the type socket.socket(socket.AF_INET, socket.SOCK_DGRAM).

    drone_socket_address        ; Socket of the Ryze Tello (IP = 192.168.10.1, port = 8889), only the port number is changable.

    Returns:

    random_direction    ; Str, calculated using another function using the random module from micropython, 
                          one of 'right', 'left', 'forward', 'back'.

    or

    Str                 ; Only one of 'right', 'left', 'forward', 'back'.
    """
    # If the RSSI is the same as the previous RSSI.
    if current_rssi == previous_rssi:
        return random_direction(UDP_server_socket, drone_socket_address, None)

    # New movement based on previous direction being right.
    elif (current_rssi > previous_rssi) and previous_direction == 'right':
        return random_direction(UDP_server_socket, drone_socket_address, 'left')

    elif (current_rssi < previous_rssi) and previous_direction == 'right':
        send_command('left 300', 10, UDP_server_socket, drone_socket_address)
        return 'left'

    # New movement based on previous direction being left.
    elif (current_rssi > previous_rssi) and previous_direction == 'left':
        return random_direction(UDP_server_socket, drone_socket_address, 'right')

    elif (current_rssi < previous_rssi) and previous_direction == 'left':
        send_command('right 300', 10, UDP_server_socket, drone_socket_address)
        return 'right'

    # New movement based on previous direction being forward.
    elif (current_rssi > previous_rssi) and previous_direction == 'forward':
        return  random_direction(UDP_server_socket, drone_socket_address, 'back')

    elif (current_rssi < previous_rssi) and previous_direction == 'forward':
        send_command('back 300', 10, UDP_server_socket, drone_socket_address)
        return 'back'

    # New movement based on previous direction being back.
    elif (current_rssi > previous_rssi) and previous_direction == 'back':
        return random_direction(UDP_server_socket, drone_socket_address, 'forward')

    elif (current_rssi < previous_rssi) and previous_direction == 'back':
        send_command('forward 300', 10, UDP_server_socket, drone_socket_address)
        return 'forward'


def random_direction(UDP_server_socket, drone_socket_address, blocked_direction):
    """
    Description:

    A function to return a random direction as a string.

    Parameters:

    UDP_server_socket   ; Var of the type socket.socket(socket.AF_INET, socket.SOCK_DGRAM).

    drone_socket_address        ; Socket of the Ryze Tello (IP = 192.168.10.1, port = 8889), only the port number is changable.

    blocked_direction   ; A direction the random function cannot return this call.

    Returns:

    direction           ; Str only one of 'right', 'left', 'forward', 'back', based on blocked_direction and the random module.
    """
    # Assign variable
    direction = None

    # Run while loop until a valid direction is chosen randomly.
    while direction == None:
        # Generate a random number and assign it to a variable.
        random_number = random.randint(1, 4)

        # Send a command to the drone socket and return direction if the block direction is not right.
        if (random_number == 1) and (blocked_direction != 'right'):
            send_command('right 300', 10, UDP_server_socket, drone_socket_address)
            direction = 'right'

        # Send a command to the drone socket and return direction if the block direction is not left.
        elif (random_number == 2) and (blocked_direction != 'left'):
            send_command('left 300', 10, UDP_server_socket, drone_socket_address)
            direction = 'left'

        # Send a command to the drone socket and return direction if the block direction is not forward.
        elif (random_number == 3) and (blocked_direction != 'forward'):
            send_command('forward 300', 10, UDP_server_socket, drone_socket_address)
            direction = 'forward'

        # Send a command to the drone socket and return direction if the block direction is not back.
        elif (random_number == 4) and (blocked_direction != 'back'):
            send_command('back 300', 10, UDP_server_socket, drone_socket_address)
            direction = 'back'

    return direction


def main():
    """
    Description:

    The main function, calls all other functions internally.
    """
    # Use the LED pin on the RaspberryPi Pico W for debugging purposes.
    LED = machine.Pin('LED', machine.Pin.OUT)

    # Assign a variable to the wlan connection between the pico W and the drone access point.
    wlan = wlan_connect_drone_ap()

    # Bind the UDP server socket and send the SDK initialization command to the drone.
    drone_communication = server_socket_bind()

    # Assign a variable to each value in the tuple returned from the server_socket_bind() function.
    UDP_server_socket = drone_communication[0]
    drone_socket_address = drone_communication[1]

    # Create an access point on the pico W.
    pico_ap = pico_access_point_create(LED)

    # Run the main data collection and communication function, this collects rssi and gps coordinates and sends it to the monitor.
    pico_data_control(LED, pico_ap, UDP_server_socket, drone_socket_address)

    # End connections when the program is finished.
    wlan_disconnect_drone_ap(wlan)
    UDP_server_socket.close()

# Start the program.
main()