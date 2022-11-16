from machine import Pin, UART

#Import utime library to implement delay
import utime, time, math

#GPS Module UART Connection
gps_module = UART(1, baudrate=9600, tx=Pin(4), rx=Pin(5))

#print gps module connection details
print(gps_module)

#Used to Store NMEA Sentences
buff = bytearray(255)

TIMEOUT = False

#store the status of satellite is fixed or not
FIX_STATUS = False

#Store GPS Coordinates
latitude = ""
longitude = ""
satellites = ""
gpsTime = ""
lat_list = []
long_list = []

#function to get gps Coordinates
def getPositionData(gps_module):
    global FIX_STATUS, TIMEOUT, latitude, longitude, satellites, gpsTime
    
    #run while loop to get gps data
    #or terminate while loop after 5 seconds timeout
    timeout = time.time() + 2   # 8 seconds from now
    while True:
        gps_module.readline()
        buff = str(gps_module.readline())
        #parse $GPGGA term
        #b'$GPGGA,094840.000,2941.8543,N,07232.5745,E,1,09,0.9,102.1,M,0.0,M,,*6C\r\n'
        #print(buff)
        parts = buff.split(',')
        
        #if no gps displayed remove "and len(parts) == 15" from below if condition
        if (parts[0] == "b'$GPGGA" and len(parts) == 15):
            if(parts[1] and parts[2] and parts[3] and parts[4] and parts[5] and parts[6] and parts[7]):
                #print("Message ID  : " + parts[0])
                #print("UTC time    : " + parts[1])
                #print("Latitude    : " + parts[2])
                #print("N/S         : " + parts[3])
                #print("Longitude   : " + parts[4])
                #print("E/W         : " + parts[5])
                #print("Position Fix: " + parts[6])
                #print("n sat       : " + parts[7])
                print(parts)
                
                latitude = convertToDigree(parts[2])
                # parts[3] contain 'N' or 'S'
                if (parts[3] == 'S'):
                    latitude = '-' + latitude
                longitude = convertToDigree(parts[4])
                # parts[5] contain 'E' or 'W'
                if (parts[5] == 'W'):
                    longitude = '-' + longitude
                satellites = parts[7]
                gpsTime = parts[1][0:2] + ":" + parts[1][2:4] + ":" + parts[1][4:6]
                FIX_STATUS = True
                break
                
        if (time.time() > timeout):
            TIMEOUT = True
            break
        utime.sleep_ms(500)
        
#function to convert raw Latitude and Longitude
#to actual Latitude and Longitude
def convertToDigree(RawDegrees):

    RawAsFloat = float(RawDegrees)
    firstdigits = int(RawAsFloat/100) #degrees
    nexttwodigits = RawAsFloat - float(firstdigits*100) #minutes
    
    Converted = float(firstdigits + nexttwodigits/60.0)
    Converted = '{0:.6f}'.format(Converted) # to 6 decimal places
    return str(Converted)
    
    
while True:
    
    getPositionData(gps_module)

    #if gps data is found then print it on lcd
    if(FIX_STATUS == True):
        print("fix......")
        
        lat = [float(latitude)]
        long = [float(longitude)]

        lat_list.append(lat)
        long_list.append(long)

        if len(lat_list) >= 15:
            
            avg_lat = sum(lat_list)/len(lat_list)
            avg_long = sum(long_list)/len(long_list)

            avg_coords = [avg_lat, avg_long]
            print(f'The average current pos coords = ({avg_coords})')

        FIX_STATUS = False
        
    if(TIMEOUT == True):
        TIMEOUT = False