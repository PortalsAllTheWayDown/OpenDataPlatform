terraform {
  required_version = ">= 1.5.7"
  backend "azurerm" {
    resource_group_name   = "state"
    storage_account_name  = "stateforterraform"
    container_name        = "state"
    key                   = "terraform.tfstate"
  }
}
 
provider "azurerm" {
  features {}
}
 
data "azurerm_client_config" "current" {}
 
#Create Resource Group
resource "azurerm_resource_group" "test" {
  name     = "testing"
  location = "eastus"
}
