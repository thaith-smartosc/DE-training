provider "azurerm" {
  features {}
  subscription_id = "571c5cf5-5725-415d-9dff-fb88e8d569a5"
}

resource "azurerm_resource_group" "d4-azure" {
  name     = "d4-azure-rg"
  location = "Southeast Asia"
}

resource "azurerm_virtual_network" "d4-azure" {
  name                = "d4-azure-vnet"
  address_space       = ["10.0.0.0/16"]
  location            = azurerm_resource_group.d4-azure.location
  resource_group_name = azurerm_resource_group.d4-azure.name
}

resource "azurerm_subnet" "d4-azure" {
  name                 = "d4-azure-subnet"
  resource_group_name  = azurerm_resource_group.d4-azure.name
  virtual_network_name = azurerm_virtual_network.d4-azure.name
  address_prefixes     = ["10.0.1.0/24"]
}

resource "azurerm_public_ip" "d4-azure" {
  name                = "d4-azure-ip"
  location            = azurerm_resource_group.d4-azure.location
  resource_group_name = azurerm_resource_group.d4-azure.name
  allocation_method   = "Dynamic"
  sku                 = "Basic"
}

resource "azurerm_network_interface" "d4-azure" {
  name                = "d4-azure-nic"
  location            = azurerm_resource_group.d4-azure.location
  resource_group_name = azurerm_resource_group.d4-azure.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.d4-azure.id
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = azurerm_public_ip.d4-azure.id
  }
}

resource "azurerm_linux_virtual_machine" "d4-azure" {
  name                = "d4-azure-vm"
  resource_group_name = azurerm_resource_group.d4-azure.name
  location            = azurerm_resource_group.d4-azure.location
  size                = "Standard_B1ls" # lowest-cost VM
  admin_username      = "azureuser"
  network_interface_ids = [
    azurerm_network_interface.d4-azure.id,
  ]

  admin_ssh_key {
    username   = "azureuser"
    public_key = file("id_rsa.pub")
  }

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Standard_LRS" # Standard HDD
  }

  source_image_reference {
    publisher = "Canonical"    # Image publisher (Canonical for Ubuntu)
    offer     = "UbuntuServer" # Image offer (Ubuntu Server)
    sku       = "18.04-LTS"    # Image SKU (Ubuntu 18.04 LTS)
    version   = "latest"       # Use the latest version of the image
  }
}

output "public_ip" {
  value = azurerm_public_ip.d4-azure.ip_address
}
