# DevOps Case Study — CSV Processor Application

A DevOps project demonstrating a full deployment for a Python Flask web application that processes CSV files and uploads them to AWS S3.

## Stack

| Layer | Technology |
|-------|-----------|
| Application | Python Flask + gunicorn |
| Reverse Proxy | nginx (sidecar container) |
| Containerization | Docker + Docker Compose |
| Orchestration | Kubernetes (kops on AWS) |
| Packaging | Helm |
| Config Management | Ansible |
| Cloud Storage | AWS S3 + Glacier lifecycle |
| Autoscaling | HPA + Cluster Autoscaler |

## Project Structure

```
devops-casestudy/
├── app/                    # Flask application, Dockerfile, nginx.conf
├── k8s/                    # Kubernetes manifests (Deployment, Service, HPA, ConfigMap)
├── helm/csv-app/           # Helm chart
├── kops/                   # Kubernetes cluster config (masters, workers, spot)
├── ansible/                # Ansible playbook and app-config role
├── s3/                     # S3 lifecycle policy
└── docker-compose.yml
```

## Local Development

```bash
# Run with Docker Compose
docker compose up --build
# Access at http://localhost:8080
```

## Kubernetes Deployment

```bash
# Create secret
kubectl create secret generic csv-app-secret \
  --from-literal=S3_BUCKET=your-bucket \
  --from-literal=AWS_ACCESS_KEY_ID=your-key \
  --from-literal=AWS_SECRET_ACCESS_KEY=your-secret \
  --from-literal=SECRET_KEY=your-flask-secret

# Deploy with Helm
helm install csv-app helm/csv-app
```

## Cluster Provisioning (kops)

```bash
export KOPS_STATE_STORE=s3://your-bucket/kops-state
kops replace -f kops/cluster.yml
kops replace -f kops/masters.yml
kops replace -f kops/nodes-ondemand.yml
kops replace -f kops/nodes-spot.yml
kops update cluster csv-app.k8s.local --yes
kops validate cluster --wait 10m
```
