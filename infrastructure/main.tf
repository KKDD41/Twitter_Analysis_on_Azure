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
}

resource "databricks_secret_scope" "eventhub-scope" {
  name = "eventhub-scope"
}

resource "databricks_secret_scope" "sqldb-scope" {
  name = "sqldb-scope"
}

resource "databricks_secret" "eventhub-conn-str" {
  key          = "eventhub-conn-str"
  string_value = azurerm_eventhub_namespace.namespace.default_primary_connection_string
  scope        = databricks_secret_scope.eventhub-scope.id
}

resource "databricks_secret" "sqldb-username" {
  key          = "sqldb-username"
  string_value = var.admin_user_name
  scope        = databricks_secret_scope.sqldb-scope.id
}

resource "databricks_secret" "sqldb-password" {
  key          = "sqldb-password"
  string_value = var.admin_user_password
  scope        = databricks_secret_scope.sqldb-scope.id
}

resource "databricks_cluster" "shared_autoscaling" {
  cluster_name  = "azure-twitter-analysis-cluster"
  spark_version = "15.4.x-scala2.12"
  spark_conf = {
    "spark.master"                     = "local[*, 4]"
    "spark.databricks.cluster.profile" = "singleNode"
    "eventhub-conn-str"                = azurerm_eventhub_namespace.namespace.default_primary_connection_string
    "sqldb-username"                   = var.admin_user_name
    "sqldb-password"                   = var.admin_user_password
  }
  node_type_id        = "Standard_D3_v2"
  driver_node_type_id = "Standard_D3_v2"
  spark_env_vars = {
    PYSPARK_PYTHON = "/databricks/python3/bin/python3"
  }
  autotermination_minutes = 120
  enable_elastic_disk     = true
  data_security_mode      = "LEGACY_SINGLE_USER_STANDARD"
  runtime_engine          = "PHOTON"
  num_workers             = 1
  depends_on = [azurerm_databricks_workspace.workspace]
}
