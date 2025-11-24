FROM python:3.10-slim

# Set working dir
WORKDIR /app

# Output prints directly to terminal 
ENV PYTHONUNBUFFERED=1

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy script
COPY . .

# Run the script
CMD ["python", "main.py"]