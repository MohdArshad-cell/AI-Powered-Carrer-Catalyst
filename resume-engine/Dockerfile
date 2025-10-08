# Use a slim Python base image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Install only the essential LaTeX packages
RUN apt-get update && apt-get install -y \
    texlive-latex-base \
    texlive-fonts-recommended \
    texlive-latex-extra \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your application code
COPY ./app ./app

# Expose the port your app runs on
EXPOSE 10000

# Command to run your application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "10000"]