output "resource_group_name" {
  value = [
    azurerm_resource_group.rg.name,
    azurerm_databricks_workspace.workspace.name
  ]
}