import math

latitude = 57.0157

longitude = 9.984072

# Conversion from degrees to radians.
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

print(f'({UTM_easting}, {UTM_northing})')

