# Use the official Python image from the DockerHub
FROM python:3.10.12

# Install OpenCV dependencies
RUN apt-get update && apt-get install -y libgl1-mesa-glx

# Install the SDL2 library
RUN apt-get update && apt-get install -y libsdl2-2.0-0

# Install support for GUI Applications
RUN apt-get update && apt-get install -y \
    libsm6 \
    libxext6 \
    libxrender-dev

# Set the working directory in docker
WORKDIR /app

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install any dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set necessary environment variables
ENV XDG_RUNTIME_DIR=/tmp/runtime-dir

# Copy the content of the local src directory to the working directory
COPY . .

# Specify the command to run on container start
CMD ["python3", "damage_detection.py"]
