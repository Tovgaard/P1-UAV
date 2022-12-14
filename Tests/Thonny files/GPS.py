from machine import Pin, UART

#Import utime library to implement delay.
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
UTM_list = []

trilateration_coords = []


#function to get gps Coordinates
def getPositionData(gps_module):
    global FIX_STATUS, TIMEOUT, latitude, longitude, satellites, gpsTime
    
    #run while loop to get gps data
    #or terminate while loop after 5 seconds timeout
    timeout = time.time()+2   # 8 seconds from now
    while True:
        gps_module.readline()
        buff = str(gps_module.readline())
        print(buff)
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

def UTM_conversion(latitude, longitude):
    # Conversion from degrees to radians
    rad_lat = latitude * (math.pi/180)
    rad_long = longitude * (math.pi/180)

    # Our UTM zone (32N)
    rad_long0 = 9*(math.pi/180)

    # Earth's equatorial radius in meters (consant)
    eq_r = 6378137

    # Earth's polar radius in meters (constant)
    pol_r = 6356752.3142

    # Scaling factor
    k0 = 0.9996

    # Different formulas to split up the final calculation
    em = math.sqrt(1-(pol_r**2/eq_r**2))

    en = (em*eq_r/pol_r)**2

    n = (eq_r-pol_r)/(eq_r+pol_r)

    rho = eq_r*(1-em**2)/(1-em**2*math.sin(rad_lat)**2)**(3/2)

    nu = eq_r/(1-em**2*math.sin(rad_lat)**2)**(1/2)

    p = (rad_long-rad_long0)

    # Calculation of the meridonial arc s:
    s = eq_r*((1-(em**2/4)-(3*em**4/64)-(5*em**6/256))*rad_lat-
        ((3*em**2/8)+(3*em**4/32)+(45*em**6/1024))*math.sin(2*rad_lat)+
        ((15*em**4/256)+(45*em**6/1024))*math.sin(4*rad_lat)-
        (35*em**6/3072)*math.sin(6*rad_lat))

    # Calculation of UTM coordinates:
    k1 = s*k0
    k2 = k0*nu*math.sin(rad_lat)*math.cos(rad_lat)/2
    k3 = (k0*nu*math.sin(rad_lat)*math.cos(rad_lat)**3/24)*(5-math.tan(rad_lat)**2+9*en*math.cos(rad_lat)**2+4*en**2*math.cos(rad_lat)**4)

    k4 = k0*nu*math.cos(rad_lat)
    k5 = (k0*nu*math.cos(rad_lat)**3/6)*(1-math.tan(rad_lat)**2+en*math.cos(rad_lat)**2)

    UTM_easting = k4*p+k5*p**3+500000
    UTM_northing = k1+k2*p**2+k3*p**4

    return [UTM_easting, UTM_northing]
    
while True:
    
    getPositionData(gps_module)

    #if gps data is found then print it on lcd
    if(FIX_STATUS == True):
        print("fix, grapping coords")
        
        lat = float(latitude)
        long = float(longitude)

        lat_list.append(lat)
        long_list.append(long)
        print(lat_list)

        if len(lat_list) >= 15:
            
            avg_lat = sum(lat_list)/len(lat_list)
            avg_long = sum(long_list)/len(long_list)

            trilateration_coords.append([avg_lat, avg_long])
            print(trilateration_coords)
            long_list = []
            lat_list = []
            utime.sleep_ms(20000)
            print('Starting new batch of GPS coords')


        if len(trilateration_coords) == 2:
            print(trilateration_coords)
            UTM_list.append(UTM_conversion(trilateration_coords[0][0], trilateration_coords[0][1]))
            UTM_list.append(UTM_conversion(trilateration_coords[1][0], trilateration_coords[1][1]))
            print(UTM_list)
            break

        FIX_STATUS = False
        
    if(TIMEOUT == True):
        TIMEOUT = False
        print('Timeout')