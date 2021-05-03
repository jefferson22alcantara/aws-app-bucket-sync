

provider "aws" {
  region = "us-east-1"
}




terraform {
  backend "s3" {
    bucket = "aws-app-bucket-sync-state"
    key    = "state/terraform.tfstate"
    region = "us-east-1"
  }
}
