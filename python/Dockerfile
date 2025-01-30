FROM python:3.10.12-slim

# Copy the requirements file in the image
COPY requirements_full.txt requirements.txt

# Install the project dependencies
RUN  pip install --upgrade pip && pip install -r requirements.txt

# Copy the project files in the image
COPY scripts /app/scripts

# Set the working directory in the image
WORKDIR /app/scripts

# Default command executed when the container starts
CMD ["python"]