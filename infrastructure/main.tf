resource "azurerm_resource_group" "rg" {
  location = var.resource_group_location
  name = "resource-group-twitter-analysis"
}

resource "azurerm_databricks_workspace" "workspace" {
  name                = "databricks-workspace-twitter-analysis"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  sku                 = "standard"

  tags = {
    Environment = "Dev"
  }
}

resource "azurerm_eventhub_namespace" "namespace" {
  name                = "eventhub-namespace-twitter-analysis"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  sku                 = "Standard"
  capacity            = 1

  tags = {
    environment = "Dev"
  }
}

resource "azurerm_eventhub" "eventhub" {
  name                = "eventhub-twitter-analysis"
  namespace_name      = azurerm_eventhub_namespace.namespace.name
  resource_group_name = azurerm_resource_group.rg.name
  partition_count     = 2
  message_retention   = 1
}