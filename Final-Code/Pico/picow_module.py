# Micropython, runs on the raspberry pi Pico W.
import network, socket, machine, utime

# Module we made, reads the GPS data and returns it as latitude longitude.
# import gps_module as gps

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


def pico_data_send(access_point):
    """
    Description:

    Creates a TCP server using the RaspberryPi Pico W, that sends data from 
    the Pico W to the monitor, when receiving a request from the client.

    Parameters:

    access_point        ; Var of the type network.WLAN(network.AP_IF).
    """
    # Create the TCP server socket.
    server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    
    # Prefered host IP of the RaspberryPi Pico W and a port for the data to stream through.
    host = '192.168.4.1'
    port = 12345

    # Bind the TCP server socket to the host IP and port.
    server_socket.bind((host, port))

    # Listen for a client on the host IP and the chosen port, only enable 1 connection.
    server_socket.listen(1)
    
    # Use the LED pin for debugging purposes.
    LED = machine.Pin('LED', machine.Pin.OUT)
    while True:
        # Accept the client if it connects to the port.
        client, address = server_socket.accept()

        while True:
            # Create a variable for the receiving request message from the client.
            return_data = client.recv(64)

            # Turn the LED on.
            LED.value(1)

            # If the request message is b'exit', close the server and end the program.
            if str(return_data) is "b'exit'":

                # Console DEBUG
                # print('Exit received, closing server!')
                
                pico_access_point_end(access_point)
                client.close()
                return
            
            # Create a UART connection between the Pico W and the GPS module, using the rx Pin GP5, 
            # (pin 7 in the datasheet a.k.a. UART1_RX, as it is receiving), on the Pico W 
            # and pin 4 (TX, as it is transmitting) on the Neo-6m GPS module.
            GPS = machine.UART(1, baudrate=9600, tx=machine.Pin(4), rx=machine.Pin(5))
            # Scan the network and assign the RSSI value to a variable.
            rssi = pico_network_scan('eduroam', 2)

            # Collect the GPS coordinates, using the module these have already been converted from NMEA to geographic coordinates.
            # coordinates = gps.get_coordinates(GPS)

            coordinates = [1, 2]
            # Make a list of the data consisting of [Latitude, Longitude, RSSI].
            data_list = [coordinates[0], coordinates[1], rssi]

            # Convert the data_list into a string and encode it so the server can send the reply in binary.
            data_str = str(data_list)
            encoded_data = data_str.encode()

            # Console DEBUG
            # print(f'Client: {client}, Address: {address}, Data: {encoded_data}.')

            # Wait a tiny bit before turning the LED on to indicate a reply with the data was send.
            utime.sleep(0.05)
            LED.value(0)
            utime.sleep(0.05)
            
            # If the request message had nothing in it break, else send the data as a reply to the client.
            if not return_data:
                break
            else:
                client.sendall(encoded_data)





def pico_network_scan(wifi_ssid, scan_amount = 10, time_between_scans = 0.1):
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


ap_pico = pico_access_point_create()

print(pico_data_send(ap_pico))