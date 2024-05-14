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
provider "azurerm" {
  skip_provider_registration = true # This is only required when the User, Service Principal, or Identity running Terraform lacks the permissions to register Azure Resource Providers.
  features {}
  client_id       = "${{secrets.AZURE_CLIENT_ID}}"
  client_secret   = "${{secrets.AZURE_CLIENT_SECRET}}"
  tenant_id       = "${{var.AZURE_TENANT_ID}}"
  subscription_id = "${{var.AZURE_SUBSCRIPTION_ID}}"
}
