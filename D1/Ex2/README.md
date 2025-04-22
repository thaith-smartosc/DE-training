# Exercise 2: Running a Flask Application in Docker on GCP VM

In this exercise, we will walk through setting up and running a Flask web application inside a Docker container on a **Google Cloud Platform (GCP) Virtual Machine (VM)**. The app will be publicly accessible through the VM’s external IP address.

## Prerequisites

- A Google Cloud account
- **Google Cloud SDK** installed on your local machine
- **GCP project** set up
- **A Google Cloud VM instance** (or created via the tutorial)
- **Docker** installed on the VM

## Step 1: Set Up a Virtual Machine on Google Cloud

1. **Create a Google Cloud Project**:
  
  - Go to [Google Cloud Console](https://console.cloud.google.com/).
  - Create a new project or select an existing one.
2. **Create a Virtual Machine (VM)**:
  
  - Go to **Compute Engine > VM Instances**.
  - Click **Create Instance**.
  - Choose an **Ubuntu** image for the instance.
  - Set a **name** for the VM.
  - Ensure the **Allow HTTP traffic** box is checked under **Firewall** settings.
3. **Access the VM**:
  
  - After the VM is created, SSH into the instance by running:
    
    ```bash
    gcloud compute ssh <YOUR_VM_NAME>
    ```
    

## Step 2: Install Docker on the VM

1. **SSH into your VM** and update the system:
  
  ```bash
  sudo apt update
  ```
  
2. **Install Docker** by running the following commands:
  
  ```bash
  sudo apt install -y apt-transport-https ca-certificates curl gnupg lsb-release
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
  echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
  sudo apt update
  sudo apt install -y docker-ce docker-ce-cli containerd.io
  ```
  
3. **Enable Docker to start automatically** and **add your user to the Docker group**:
  
  ```bash
  sudo systemctl enable docker
  sudo usermod -aG docker $USER
  ```
  
4. **Log out and log back in** to apply the group changes.
  

---

## Step 3: Prepare the Flask Application

1. **Create a Flask app** (`app.py`) on your local machine or directly in the VM:
  
  ```python
  from flask import Flask
  app = Flask(__name__)
  
  @app.route("/")
  def hello():
      return "Hello, World from Docker on GCP VM!"
  
  if __name__ == "__main__":
      app.run(host="0.0.0.0", port=8080)
  ```
  
2. **Create a requirements.txt** to define the dependencies for the Flask app:
  
  ```
  Flask==2.1.2
  ```
  

---

## Step 4: Dockerize the Flask Application

1. **Create a Dockerfile** in the same directory as your `app.py` and `requirements.txt`:
  
  ```dockerfile
  # Use official Python image from Docker Hub
  FROM python:3.9-slim
  
  # Set the working directory
  WORKDIR /app
  
  # Install dependencies
  COPY requirements.txt .
  RUN pip install --no-cache-dir -r requirements.txt
  
  # Copy application files to the container
  COPY . .
  
  # Expose port Flask is running on
  EXPOSE 8080
  
  # Command to run the application
  CMD ["python", "app.py"]
  ```
  
2. **Build the Docker image**:
  
  In the same directory as your `Dockerfile`, run:
  
  ```bash
  docker build -t flask-docker-app .
  ```
  

---

## Step 5: Run the Docker Container

1. **Run the Flask application** inside Docker on your VM:
  
  ```bash
  docker run -d -p 80:8080 flask-docker-app
  ```
  
2. **Verify the container is running** by checking:
  
  ```bash
  docker ps
  ```
  
  Ensure you see your container running with `0.0.0.0:80->8080/tcp`.
  

---

## Step 6: Open Firewall on GCP to Allow External Traffic

1. **Allow HTTP traffic** through the Google Cloud Firewall:
  
  - Go to **VPC Network > Firewall Rules**.
  - Create a new rule to allow traffic on port 80 (HTTP).
  
  Alternatively, run this command:
  
  ```bash
  gcloud compute firewall-rules create allow-http      --allow tcp:80      --source-ranges=0.0.0.0/0      --target-tags=http-server      --description="Allow HTTP traffic on port 80"
  ```
  
2. **Tag the VM** with `http-server` to apply the firewall rule.
  

---

## Step 7: Access Your Application

1. **Get the external IP address** of your VM:
  
  - In the **VM Instances** page, locate the external IP address of your instance.
2. **Access the Flask app** by navigating to:
  
  ```
  http://<EXTERNAL_IP>
  ```
  
  You should see the message:
  
  ```
  Hello, World from Docker on GCP VM!
  ```
  
