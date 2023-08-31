# Slim version of Python
FROM python:3.8.12-slim

# Download Package Information
RUN apt-get update -y

# Install Tkinter
RUN pip install paho-mqtt
RUN apt-get install tk -y

# Commands to run Tkinter application
CMD ["dashboard.py"]
ENTRYPOINT ["python3"]