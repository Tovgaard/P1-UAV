#%%

# distance monitor.
import math, matplotlib.pylab as plt

list1 = [-68.86667, -65.2, -60.13334, -53.66667, -75.43333, -68.63333, -64.53333, -54.6, -69.1, -66.26667, -59.23333, -53.13334, -70.2, -64.7, -62.53333, -55.43333]
list2 =[]

MHz = 2400+5*6
FSPL = 27.57 #27.55
environmental_constant = 20.77

for i in range(len(list1)):
    dBm = list1[i]
    m = 10 ** (( FSPL - (environmental_constant * math.log10(MHz+1)) + abs(dBm) ) / 20 )
    list2.append(m)

print(f'Øst: {list2[0], list2[1], list2[2], list2[3]}\nVest: {list2[4], list2[5], list2[6], list2[7]}\nSyd: {list2[8], list2[9], list2[10], list2[11]}\nNord: {list2[12], list2[13], list2[14], list2[15]}\n')
print(f'20m difference: min: {20-min(list2[0],list2[8],list2[12])}, max: {20-max(list2[0],list2[8],list2[12])}')
print(f'15m difference: min: {15-min(list2[1],list2[9],list2[13])}, max: {15-max(list2[1],list2[9],list2[13])}')
print(f'10m difference: min: {10-min(list2[2],list2[10],list2[14])}, max: {10-max(list2[2],list2[10],list2[14])}')
print(f'5m difference: min: {5-min(list2[3],list2[11],list2[15])}, max: {5-max(list2[3],list2[11],list2[15])}\n')

truth_coefficient = abs(20-min(list2[0],list2[8],list2[12]))+abs(20-max(list2[0],list2[8],list2[12]))+abs(15-min(list2[1],list2[9],list2[13]))+abs(15-max(list2[1],list2[9],list2[13]))+abs(10-min(list2[2],list2[10],list2[14]))+abs(10-max(list2[2],list2[10],list2[14]))+abs(5-min(list2[3],list2[11],list2[15]))+abs(5-max(list2[3],list2[11],list2[15]))

# 0 = 100% accurate
print(truth_coefficient)

y = list2
x = range(1, len(y)+1)

plt.plot(x,y, label='meter')
plt.grid(linestyle=':')
plt.legend()
plt.show

# %%
