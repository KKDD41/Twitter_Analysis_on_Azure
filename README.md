# Twitter Analysis on Azure

Pet-project aimed to show and master fully-automated ETL-pipeline creation in Microsoft Azure. 
As sample data were taken Elon Musk tweets (through `tweepy` X API V2, but also dummy data is available).

### Pipeline Structure

1. `producer.py` as a simple app generating tweets and transfer them into Azure Event Hub.
2. Databricks spark-streaming job `etl-twitter-analysis.py` / `etl-twitter-analysis.ipynb` aggregates incoming events from Azure Event Hub
and writes summarized data into Azure SQL Database.

### Deployment

Resources deployment is fully automated. Prerequisites are Terraform, Azure CLI (with personal account created) and Databricks CLI.

Infrastructure deployment:
```commandline
cd infrastructure
terraform init -upgrade
terraform plan -out main.tfplan
terraform apply main.tfplan
```

Resources clean-up:
```commandline
terraform plan -destroy -out main.destroy.tfplan
terraform apply main.destroy.tfplan
```
