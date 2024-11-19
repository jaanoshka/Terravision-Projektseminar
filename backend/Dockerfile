# Dockerfile for Flask backend with Open3D
FROM python:3.10

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libxi6 \
    libxrender1 \
    libxrandr2 \
    libx11-6 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy requirements and install them
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install  --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

EXPOSE 4000

# Start the application
CMD ["flask", "run", "--host=0.0.0.0","--port=4000"]