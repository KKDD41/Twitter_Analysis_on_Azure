resource "azurerm_resource_group" "rg" {
  location = var.resource_group_location
  name     = "resource-group-twitter-analysis"
}

resource "azurerm_databricks_workspace" "workspace" {
  name                = "databricks-workspace-twitter-analysis"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  sku                 = "standard"

  tags = {
    Environment = var.environment_tag
  }
}

resource "azurerm_eventhub_namespace" "namespace" {
  name                = "eventhub-namespace-twitter-analysis"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  sku                 = "Standard"
  capacity            = 1

  tags = {
    Environment = var.environment_tag
  }
}

resource "azurerm_eventhub" "eventhub" {
  name                = "eventhub-twitter-analysis"
  namespace_name      = azurerm_eventhub_namespace.namespace.name
  resource_group_name = azurerm_resource_group.rg.name
  partition_count     = 2
  message_retention   = 1
}

resource "azurerm_mssql_server" "sqlserver" {
  name                         = "sqlserver-twitter-analysis"
  resource_group_name          = azurerm_resource_group.rg.name
  location                     = azurerm_resource_group.rg.location
  administrator_login          = var.admin_user_name
  administrator_login_password = var.admin_user_password
  version                      = "12.0"

  tags = {
    Environment = var.environment_tag
  }
}

resource "azurerm_mssql_database" "db" {
  name      = "db-twitter-analysis"
  server_id = azurerm_mssql_server.sqlserver.id

  tags = {
    Environment = var.environment_tag
  }
}

resource "azurerm_mssql_firewall_rule" "firewall" {
  name             = "allow-azure-service"
  server_id        = azurerm_mssql_server.sqlserver.id
  start_ip_address = "0.0.0.0"
  end_ip_address   = "0.0.0.0"

  tags = {
    Environment = var.environment_tag
  }
}
