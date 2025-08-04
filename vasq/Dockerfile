# Official Python runtime for parent image
FROM python:3.10

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set working directory inside container
WORKDIR /app

# Install system libraries required for Python packages
RUN apt-get update && apt-get install -y \
    gcc \
    gfortran \
    g++ \
    libblas-dev \
    libhdf5-dev \
    liblapack-dev \
    libopenblas-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy current directory contents into container
COPY . /app

# Install requirements
RUN pip install --upgrade pip && pip install -r requirements.txt

# Make port 8000 available to world outside container
EXPOSE 8000

# Run the Django development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
