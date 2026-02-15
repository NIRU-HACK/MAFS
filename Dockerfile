ARG BASE_IMAGE=python:3.11-slim
FROM ${BASE_IMAGE}

# Install system dependencies for OpenCV and Matplotlib and clean up apt cache
RUN apt-get update && apt-get install -y \
    ffmpeg libsm6 libxext6 \
 && rm -rf /var/lib/apt/lists/* 


WORKDIR /app

# Install system dependencies for OpenCV and Matplotlib
RUN apt-get update && apt-get install -y \
    ffmpeg libsm6 libxext6 \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip 
RUN pip install --no-cache-dir -r requirements.txt
#Web Interface (UI)
COPY ["Final Web Application/", "./Final Web Application/"]
#Prepare Images
COPY Preprocessing/ ./Preprocessing/
#Logic(Model and Tracking)
COPY ["Inference and Implementation/", "./Inference and Implementation/"]

# Expose the port
EXPOSE 8501

# Command to run the app
# Update the path to point to where your main streamlit file is located
# Example: "Final Web Application/main.py"
CMD ["streamlit", "run", "Final Web Application/main.py", "--server.port=8501", "--server.address=0.0.0.0"]