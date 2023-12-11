
def extract_timestamp(filename):
    # Debug
    # print(f"Extracting timestamp from file: {filename}")

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
    # Debug
    # print(f"Extracted timestamp: {total_seconds}, Type: {type(total_seconds)}")
    return total_seconds

