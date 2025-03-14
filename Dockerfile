# Use an official Python runtime as the base image
FROM python:3.9-slim

# Install system dependencies and Google Chrome
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    libglib2.0-0 \
    libnss3 \
    libgconf-2-4 \
    libfontconfig1 \
    libxrender1 \
    libxtst6 \
    libxi6 \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    # Debug: Find and verify Chrome binary
    && CHROME_PATH=$(which google-chrome || which google-chrome-stable || echo "Chrome not found!") \
    && echo "Chrome binary path: $CHROME_PATH" \
    && test -f "$CHROME_PATH" && $CHROME_PATH --version || echo "Chrome binary not executable or missing!" \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set environment variable for Chrome binary path
ENV CHROME_BINARY_PATH=$CHROME_PATH

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the bot script
COPY bot.py .

# Run the bot
CMD ["python", "bot.py"]