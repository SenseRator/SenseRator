def extract_timestamp(filename):
    try:
        # Splitting the filename and extracting time components
        components = filename.split('_')[1:]
        components = components[:5] + components[5].split('.')[:2]

        # Converting the time components to floats
        hour, minute, second, milliseconds = map(float, components[3:7])

        # Calculating total seconds
        total_seconds = hour * 3600 + minute * 60 + second + milliseconds * 0.0001

        return total_seconds

    except (IndexError, ValueError) as e:
        # Handling potential errors in filename parsing or value conversion
        print(f"Error extracting timestamp from '{filename}': {e}")
        return None