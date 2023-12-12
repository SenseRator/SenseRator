import time

def extract_timestamp(filename):
    # Split the filename by underscores and period to get timestamp components
    components = filename.split('_')[:6] + filename.split('_')[6].split('.')[:2]

    # Convert the timestamp components to integers
    year, month, day, hour, minute, second, milliseconds = map(int, components)

    # Calculate the total seconds
    total_seconds = (
        year * 365 * 24 * 60 * 60 +
        month * 30 * 24 * 60 * 60 +
        day * 24 * 60 * 60 +
        hour * 60 * 60 +
        minute * 60 +
        second +
        milliseconds / 10000
    )

    return total_seconds

t1 = extract_timestamp('lidar_2023_11_18_15_39_28.6313.jpg')
t2 = extract_timestamp('lidar_2023_11_18_15_53_10.1271.jpg')


print(t2 - t1)
t = time.time()
time.sleep(t2-t1)
print(time.time() - t)

