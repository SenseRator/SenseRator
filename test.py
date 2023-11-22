import time

def timestamp(filename):
    ts = filename.split('_')[1:]
    ts = ts[:5]+ts[5].split('.')[:2]
    s = float(ts[2]) * (24 * 60 * 60) + float(ts[3]) * (60 * 60) + float(ts[4]) * 60 + float(ts[5]) * 1 + float(ts[6]) * .0001
    
    return s

t1 = timestamp('lidar_2023_11_18_15_39_28.6313.jpg')
t2 = timestamp('lidar_2023_11_18_15_53_10.1271.jpg')


print(t2 - t1)
t = time.time()
time.sleep(t2-t1)
print(time.time() - t)

