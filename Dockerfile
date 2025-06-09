# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies that some python packages might need
RUN apt-get update && apt-get install -y build-essential

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code into the container
COPY ./echosphere ./echosphere

# Make port 8080 available to the world outside this container
EXPOSE 8080

# Define the command to run the application
# This runs Gunicorn, a production-ready web server
CMD ["gunicorn", "--bind", ":8080", "--workers", "1", "--threads", "4", "echosphere.app:app"]
