output "storage_account_name" {
  value = azurerm_storage_account.datalake.name
}

output "container_url" {
  value = azurerm_storage_container.datalake_container.id
}
