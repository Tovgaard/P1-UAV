# import module
import os

# function to establish a new connection
def createNewConnection(name, SSID, password):

	command = "netsh wlan add profile filename=\""+name+".xml\""+" interface=Wi-Fi"
	os.system(command)

# function to connect to a network
def connect(name, SSID):
	command = "netsh wlan connect name=\""+name+"\" ssid=\""+SSID+"\" interface=Wi-Fi"
	os.system(command)

# function to display avavilabe Wifi networks
def displayAvailableNetworks():
	command = "netsh wlan show networks interface=Wi-Fi"
	os.system(command)


# display available networks
displayAvailableNetworks()

# input wifi name and password
name = input("Name of Wi-Fi: ")
password = input("Password: ")

# establish new connection
createNewConnection(name, name, password)

# connect to the wifi network
connect(name, name)
print("If you aren't connected to this network, try connecting with the correct password!")
