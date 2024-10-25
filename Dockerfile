# Base image with Python and Cron
FROM python:3.9-slim

# Set environment variables for logging
ENV PYTHONUNBUFFERED=1

# Set the working directory inside the container
WORKDIR /app

# Copy only necessary files to leverage Docker cache
COPY ./cron_job/run_job.py .
COPY ./cron_job/main.py .
COPY ../.env /app/.env

# Make the run_job.py file executable
RUN chmod +x run_job.py

# Install required Python libraries (assuming you have a requirements file)
COPY requirements.txt .
RUN pip install -r requirements.txt

# Install cron
RUN apt-get update && apt-get install -y cron

# Add a cron job for running the Python script every minute for testing
RUN echo "*/2 * * * * python /app/run_job.py >> /app/cron.log 2>&1" > /etc/cron.d/my-cron-job

# Give execution rights on the cron job
RUN chmod 0644 /etc/cron.d/my-cron-job

# Apply cron job
RUN crontab /etc/cron.d/my-cron-job

# Add logging to console
CMD cron && tail -f /app/cron.log

# Persist cron logs
VOLUME /app/cron.log

# Run the command on container startup
CMD ["cron", "-f"]
