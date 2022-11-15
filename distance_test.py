
from math import log10
import network

test_amount = 30
wifi_name = 'Bear'

wifi_avg_list = []

def network_scan():
    for scans in range(test_amount):
        wlan = network.WLAN()
        networks = wlan.scan()

        for w in networks:
            if w[0].decode() == wifi_name:
                wifi_avg_list.append(w[3])
                print(w[3])
            else:
                print('Network was not found')

    if len(wifi_avg_list) >= 2: # normally 5     
        avg_dBm = sum(wifi_avg_list)/len(wifi_avg_list)
        return avg_dBm
    else:
        return None

def cal_distance(dBm):

    if dBm != None:
        MHz = 2400
        FSPL = 27.55

        m = 10 ** (( FSPL - (20 * log10(MHz)) + abs(dBm) ) / 20 )
        m=round(m,2)
        
        print(f'wifi name = {wifi_name}')
        print(f'Collected RSSI data: {wifi_avg_list}')
        print(f'Average RSSI = {dBm}\n Distance to access point = {m}m\n amount of succeded tests: {len(wifi_avg_list)}/{test_amount} \n afvigelse = {abs(min(wifi_avg_list))-abs(max(wifi_avg_list))}')
    else:
        print('To few connections <= 5')

cal_distance(network_scan())

