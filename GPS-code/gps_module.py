from machine import UART, Pin
import utime
"""
Description:

Module for getting and converting coordinates from the Ublox GPS module.
"""

# GPS Module UART Connection.
gps = UART(1, baudrate=9600, tx=Pin(4), rx=Pin(5))

def get_coordinates(gps_module):
    """
    Description:

    A function to extract Latitude and Longitude from a Ublox Neo-6m GPS module.

    Parameters:

    gps_module          ; UART, takes an UART connection from machine import, an build in library in micropython.

    Returns:

    List       ; [float Latitude, float Longitude], returns a list containing the GPS position in Latitude and Longitude.
    """
    while True:
        # Sleeps 0,08s otherwise NMEA sentences are not returned in one sentence.
        utime.sleep(0.08)

        # Array for storing NMEA sentences.
        NMEA_array = bytearray(255)

        # Read the array
        NMEA_array = str(gps_module.readline())

        # Split the message using ','.
        NMEA_sentence = NMEA_array.split(',')
        print(NMEA_sentence)
        # Check if it is the right NMEA sentence (the one with coordinates).
        if NMEA_sentence[0] is "b'$GPGGA":
            if (NMEA_sentence[3] is ('N' or 'S')) and (NMEA_sentence[5] is ('E' or 'W')):
                latitude = decimal_degree_converter(NMEA_sentence[2], NMEA_sentence[3])
                longitude = decimal_degree_converter(NMEA_sentence[4], NMEA_sentence[5])

                return [latitude, longitude]

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

# print(get_coordinates(gps))

# Source (decimal conversion): https://forums.raspberrypi.com/viewtopic.php?t=175163o