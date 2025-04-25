provider "azurerm" {
  features {}
  subscription_id = "571c5cf5-5725-415d-9dff-fb88e8d569a5"
}

resource "azurerm_resource_group" "data_rg" {
  name     = var.resource_group_name
  location = var.location
}

resource "azurerm_storage_account" "datalake" {
  name                     = var.storage_account_name
  resource_group_name      = azurerm_resource_group.data_rg.name
  location                 = azurerm_resource_group.data_rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  is_hns_enabled           = true # Hierarchical namespace for Data Lake Gen2
}

# Create the Synapse Resource Group (if not already created)
resource "azurerm_resource_group" "thaith_synapse" {
  name     = "thaith-synapse-rg"
  location = var.location
}

resource "azurerm_storage_container" "datalake_container" {
  name                  = var.container_name
  storage_account_name  = azurerm_storage_account.datalake.name
  container_access_type = "blob"
}

# Synapse Workspace
resource "azurerm_synapse_workspace" "thaith_synapse" {
  name                                 = "thaith-synapse"
  resource_group_name                  = azurerm_resource_group.thaith_synapse.name
  location                             = azurerm_resource_group.thaith_synapse.location
  storage_data_lake_gen2_filesystem_id = "https://${azurerm_storage_account.datalake.name}.dfs.core.windows.net/${azurerm_storage_container.datalake_container.name}"

  sql_administrator_login              = "sqladminuser"
  sql_administrator_login_password     = "Your-StrongP@ssw0rd"

  identity {
    type = "SystemAssigned"
  }
}

# Synapse SQL Pool
resource "azurerm_synapse_sql_pool" "thaith_sql_pool" {
  name                  = "thaith_sql_pool"  # Updated name to be valid
  synapse_workspace_id  = azurerm_synapse_workspace.thaith_synapse.id
  storage_account_type  = "GRS"  # Use "LRS" or "GRS"

  sku_name = "DW100c"
}

