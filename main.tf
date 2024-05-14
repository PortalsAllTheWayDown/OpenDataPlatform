terraform {
  backend "azurerm" {
    resource_group_name   = "state"
    storage_account_name  = "stateforterraform"
    container_name        = "state"
    key                   = "terraform.tfstate"
  }
}
terraform {
  required_version = ">= 1.5.7"
  backend "azurerm" {
    resource_group_name  = "thomasthorntoncloud"
    storage_account_name = "thomasthorntontfstate"
    container_name       = "github-thomasthorntoncloud-terraform-example"
    key                  = "github-thomasthorntoncloud-terraform-example.tfstate"
  }
}
 
provider "azurerm" {
  features {}
}
 
data "azurerm_client_config" "current" {}
 
#Create Resource Group
resource "azurerm_resource_group" "tamops" {
  name     = "github-thomasthorntoncloud-terraform-example"
  location = "uksouth"
}
