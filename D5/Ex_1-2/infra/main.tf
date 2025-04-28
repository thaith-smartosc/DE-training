provider "azurerm" {
  features {}
  subscription_id = "571c5cf5-5725-415d-9dff-fb88e8d569a5"
}

resource "azurerm_resource_group" "rg" {
  name     = "thaith-flask-app-rg"
  location = "southeastasia"
}

resource "azurerm_postgresql_flexible_server" "db" {
  name                         = "mypgserver12345"
  resource_group_name          = azurerm_resource_group.rg.name
  location                     = azurerm_resource_group.rg.location
  administrator_login          = "myuser"
  administrator_password       = "mypassword"
  version                      = "13"
  storage_mb                   = 32768
  sku_name                     = "B_Standard_B1ms"
  backup_retention_days        = 7
  geo_redundant_backup_enabled = false
  zone                         = "1"

  authentication {
    active_directory_auth_enabled = false
    password_auth_enabled         = true
  }
}

resource "azurerm_container_registry" "acr" {
  name                = "flaskappacr123"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  sku                 = "Basic"
  admin_enabled       = true
}

resource "azurerm_container_group" "app" {
  name                = "flask-app-container"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  os_type             = "Linux"

  image_registry_credential {
    server   = "flaskappacr123.azurecr.io"
    username = "flaskappacr123"
    password = "password123"
  }

  container {
    name   = "flaskapp"
    image  = "flaskappacr123.azurecr.io/flaskapp:latest"
    cpu    = "0.5"
    memory = "1.0"

    ports {
      port     = 5000
      protocol = "TCP"
    }

    environment_variables = {
      DB_HOST     = azurerm_postgresql_flexible_server.db.fqdn
      DB_USER     = "myuser"
      DB_PASSWORD = "mypassword"
      DB_NAME     = "postgres"
      FORCE_REDEPLOY = timestamp()
    }
  }

  ip_address_type = "Public"
  dns_name_label  = "flaskappdemo123"

  restart_policy = "Always"

  lifecycle {
    create_before_destroy = true
  }
}
