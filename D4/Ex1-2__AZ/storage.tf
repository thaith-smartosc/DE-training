# Create an Azure Storage Account
resource "azurerm_storage_account" "d4-azure" {
  name                     = "d4azurestoracc"  # Ensure this name is globally unique
  resource_group_name      = azurerm_resource_group.d4-azure.name
  location                 = azurerm_resource_group.d4-azure.location
  account_tier             = "Standard"
  account_replication_type = "LRS"

  # Access tier for the blob storage
  access_tier = "Hot"
}

# Create a Storage Container inside the Storage Account
resource "azurerm_storage_container" "d4-azure" {
  name                  = "d4-azure-container"
  storage_account_name  = azurerm_storage_account.d4-azure.name
  container_access_type = "blob"
}