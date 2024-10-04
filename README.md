# Twitter_Sentiment_Analysis_on_Azure

Deployment:

```commandline
cd terraform
az login
cd infrastructure
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
1. Create compute resource Databricks general-purpose cluster: `Standard_D3_v2`, runtime: `15.4 LTS`.
2. 