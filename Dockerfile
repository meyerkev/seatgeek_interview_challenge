# Use the official image as a parent image.
FROM python:3.9.0

# Set the working directory.
WORKDIR /usr/src/app

# Copy the file from your host to your current location.
# Copy the rest of your app's source code from your host to your image filesystem.
COPY src/ src/
COPY data/ data/

# Set and install python dependencies
COPY requirements.txt requirements.txt

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Add metadata to the image to describe which port the container is listening on at runtime.
EXPOSE 8080

# Run the specified command within the container.
CMD [ "python", "src/server.py" ]


