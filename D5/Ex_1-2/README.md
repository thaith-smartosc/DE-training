
# Exercise 1: Dockerized Flask Application with PostgreSQL Backend on Azure

This exercise demonstrates how to build a **Dockerized Flask application** with a **PostgreSQL backend** and deploy it using **Terraform** on **Azure**. The steps outlined below guide you through creating a Docker container for the app, setting up PostgreSQL, and deploying it on Azure.

---

## Prerequisites

Before starting, ensure you have the following installed on your local machine:

- [Docker](https://www.docker.com/get-started)
- [Terraform](https://www.terraform.io/downloads.html)
- [Azure CLI](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli)
- [Python 3.x](https://www.python.org/downloads/)

Additionally, you'll need:

- An **Azure account** (if you don't have one, sign up at [Azure](https://azure.microsoft.com/en-us/free/)).

---

## Steps

### Step 1: Set up PostgreSQL

1. **Create a Docker container for PostgreSQL**:
   
   In your terminal, run the following command to start a PostgreSQL container:

   ```bash
   docker run --name my-postgres      -e POSTGRES_USER=myuser      -e POSTGRES_PASSWORD=mypassword      -e POSTGRES_DB=mydatabase      -p 5432:5432      -d postgres
   ```

   This command will:
   - Set up the `myuser` as the PostgreSQL user.
   - Set up the password as `mypassword`.
   - Create a database called `mydatabase`.
   - Expose port `5432` for connections.

2. **Verify the PostgreSQL container**:
   Run `docker ps` to ensure the container is running. You should see `my-postgres` listed as an active container.

---

### Step 2: Dockerize Flask Application

1. **Create a Flask app**:
   Create a simple `app.py` file for your Flask application:

   ```python
   from flask import Flask, jsonify
   import psycopg2

   app = Flask(__name__)

   @app.route('/')
   def hello():
       return jsonify({"message": "Hello from Flask and PostgreSQL!"})

   if __name__ == '__main__':
       app.run(host='0.0.0.0', port=5000)
   ```

2. **Create a `requirements.txt` file**:
   List the dependencies for the Flask app in `requirements.txt`:

   ```
   Flask==3.1.0
   psycopg2-binary
   ```

3. **Create a `Dockerfile`**:
   The `Dockerfile` will containerize the Flask app:

   ```dockerfile
   FROM python:3.11-slim

   WORKDIR /app

   COPY requirements.txt .

   RUN apt-get update && apt-get install -y gcc libpq-dev
   RUN pip install --no-cache-dir -r requirements.txt

   COPY . .

   CMD ["python", "app.py"]
   ```

4. **Build and run the Docker container**:
   Build the Flask app Docker image:

   ```bash
   docker build -t flask-app .
   ```

   Run the Flask app container:

   ```bash
   docker run -p 5000:5000 --link my-postgres:postgres flask-app
   ```

---

### Step 3: Set up Terraform Deployment on Azure

1. **Create Terraform configuration files**:

   - **`main.tf`**: Defines resources for your Azure environment.

   ```hcl
   provider "azurerm" {
     features {}
   }

   resource "azurerm_resource_group" "example" {
     name     = "example-resources"
     location = "East US"
   }

   resource "azurerm_container_registry" "example" {
     name                = "exampleacr"
     resource_group_name = azurerm_resource_group.example.name
     location            = azurerm_resource_group.example.location
     sku                 = "Basic"
   }

   resource "azurerm_container_group" "example" {
     name                = "example-containergroup"
     location            = azurerm_resource_group.example.location
     resource_group_name = azurerm_resource_group.example.name

     containers {
       name   = "flask-container"
       image  = "your-acr-name.azurecr.io/flask-app:latest"
       cpu    = "0.5"
       memory = "1.5"

       ports {
         port     = 5000
         protocol = "TCP"
       }
     }

     tags = {
       environment = "testing"
     }
   }
   ```

2. **Initialize Terraform**:
   Run the following to initialize the Terraform configuration:

   ```bash
   terraform init
   ```

3. **Apply the Terraform plan**:
   Run the following to apply the configuration and deploy the resources:

   ```bash
   terraform apply
   ```

   After the resources are created, Terraform will output the public IP of your container group.

---

### Step 4: Push Docker Image to Azure Container Registry

1. **Login to your Azure Container Registry (ACR)**:

   ```bash
   az acr login --name <your-acr-name>
   ```

2. **Tag and push the Docker image**:

   Tag the Docker image with your ACR URL:

   ```bash
   docker tag flask-app:latest <your-acr-name>.azurecr.io/flask-app:latest
   ```

   Push the image to ACR:

   ```bash
   docker push <your-acr-name>.azurecr.io/flask-app:latest
   ```

---

### Step 5: Access the Application

Once the deployment is complete, navigate to the public IP address provided by Terraform, and you should see:

```json
{
  "message": "Hello from Flask and PostgreSQL!"
}
```

---

## Troubleshooting

- **Error: `pg_config executable not found`**: If you encounter this issue during the build process, ensure that you install `libpq-dev` and `gcc` in your Dockerfile to enable the `psycopg2` package to build.
- **PostgreSQL connection issues**: Make sure the Flask app is connecting to the correct hostname and port of the PostgreSQL container or ACR instance.

---

## Conclusion

In this exercise, you:

- Created a Dockerized Flask app with a PostgreSQL backend.
- Deployed it using Azure and Terraform.
- Pushed the Docker image to Azure Container Registry.

This setup provides a scalable and reliable environment for running Flask apps with a PostgreSQL database on Azure. 

---
