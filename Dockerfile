# Use the official image as a parent image.
FROM ubuntu:latest

RUN apt-get update \
    && apt-get install apt-utils \
    && apt-get upgrade -y

RUN apt-get install -y python3 python-is-python3

# Set the working directory.
WORKDIR /usr/src/app

# Copy the file from your host to your current location.
# Copy the rest of your app's source code from your host to your image filesystem.
COPY src/ src/

# We have no Python dependencies as per request
# Normally, install requirements.txt

# Add metadata to the image to describe which port the container is listening on at runtime.
EXPOSE 8099

# Run the specified command within the container.
CMD [ "python", "src/server.py" ]


