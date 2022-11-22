import math

lat1 = 57.014897
lon1 = 9.983773

lat2 = 57.015385
lon2 = 9.984412


radius = 6371
φ1 = lat1 * math.pi/180; # φ, λ in radians
φ2 = lat2 * math.pi/180
Δφ = (lat2-lat1) * math.pi/180
Δλ = (lon2-lon1) * math.pi/180

a = math.sin(Δφ/2) * math.sin(Δφ/2) + math.cos(φ1) * math.cos(φ2) * math.sin(Δλ/2) * math.sin(Δλ/2)

c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

dist = radius * c * 1000

print(f'The distance between the 2 geographic coordinates is: {dist}m')


