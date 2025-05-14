FROM bitnami/spark:3.4.1

# Install Python dependencies
RUN pip install google-cloud-storage google-cloud-bigquery pandas py4j

# Copy your Spark app
COPY . /app
WORKDIR /app

# Default command
CMD ["python", "loyalty_anlyzer.py"]
