
from math import log10
import network, time


def network_scan(scan_amount = 60, wifi_name = 'LenovoFalk', time_between_network_scans = 0.1):
    channel_received = False
    wifi_avg_list = []
    channel = []

    wlan = network.WLAN()
    wlan.active(True)

    while channel_received == False:
        networks = wlan.scan()
        for w in networks:
            if w[0].decode() == wifi_name:
                channel.append(w[2])
                channel_received = True
                print(f'Access point {wifi_name} found!')

    while True:
        networks = wlan.scan()

        for w in networks:
            if w[0].decode() == wifi_name:
                wifi_avg_list.append(w[3])
                channel.append(w[2])
        
        time.sleep(time_between_network_scans)

        if len(wifi_avg_list) >= scan_amount: 
            avg_dBm = sum(wifi_avg_list)/len(wifi_avg_list)
            return [channel, avg_dBm, wifi_avg_list, wifi_name]

def cal_distance(wifi_info):
    if wifi_info[1] != None:
        wifi_frequency = 2412+5*(wifi_info[0][0]-1)
        FSPL = 27.55 #27.55

        m = 10 ** (( FSPL - (20 * log10(wifi_frequency)) + abs(wifi_info[1]) ) / 20 )
        m=round(m,2)
        
        # Debug
        print(f'wifi name = {wifi_info[3]}, channel = {wifi_info[0][0]}')
        print(f'Collected RSSI data: {wifi_info[2]}')
        print(f'Average RSSI = {wifi_info[1]}\nDistance to access point = {m}m\nmin = {min(wifi_info[2])}, max = {max(wifi_info[2])}')

        return m

(cal_distance(network_scan(scan_amount = 30, wifi_name = 'LenovoFalk')))


