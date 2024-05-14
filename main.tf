terraform {
  backend "azurerm" {
    resource_group_name   = "state"
    storage_account_name  = "stateforterraform"
    container_name        = "state"
    key                   = "terraform.tfstate"
  }
}
resource "azurerm_resource_group" "opendataplatform" {
  name     = "OpenDataPlatform"
  location = "East US"
}
terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "=3.0.0"
    }
  }
}
data "azurerm_client_config" "current" {}
provider "azurerm" {
  features {}
}
