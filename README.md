# Twitter_Sentiment_Analysis_on_Azure

Deployment:

```commandline
cd terraform
az login
terraform init -upgrade
terraform plan -out main.tfplan
terraform apply main.tfplan
```

Deletion:
```commandline
terraform plan -destroy -out main.destroy.tfplan
terraform apply main.destroy.tfplan
```

Databricks workspace configuration:
1. Create compute resource.
2. Install library https://learn.microsoft.com/en-us/azure/databricks/archive/azure/streaming-event-hubs.
3. 