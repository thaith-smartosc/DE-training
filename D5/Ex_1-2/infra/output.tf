output "flask_app_url" {
  value = "http://${azurerm_container_group.app.ip_address}:5000"
}
