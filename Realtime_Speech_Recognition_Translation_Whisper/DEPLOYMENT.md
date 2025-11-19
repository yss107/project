# Cloud Deployment Guide

## Overview

This guide provides step-by-step instructions for deploying the Whisper Real-time Speech Recognition & Translation system to various cloud platforms.

## Table of Contents

1. [Docker Deployment](#docker-deployment)
2. [Kubernetes Deployment](#kubernetes-deployment)
3. [AWS Deployment](#aws-deployment)
4. [Google Cloud Platform](#google-cloud-platform)
5. [Azure Deployment](#azure-deployment)
6. [DigitalOcean Deployment](#digitalocean-deployment)

---

## Docker Deployment

### Prerequisites

- Docker installed
- Docker Compose installed

### Build Images

```bash
# Build CPU image
docker build -t whisper-api:latest -f Dockerfile .

# Build GPU image (requires NVIDIA Docker runtime)
docker build -t whisper-api-gpu:latest -f Dockerfile.gpu .
```

### Run with Docker Compose

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Configuration

Create `.env` file:

```env
WANDB_API_KEY=your_wandb_key
HF_TOKEN=your_huggingface_token
TARGET_LANGUAGE=es
USE_WANDB=false
```

### Access the API

- CPU Service: `http://localhost:8000`
- GPU Service: `http://localhost:8001`
- API Docs: `http://localhost:8000/docs`

---

## Kubernetes Deployment

### Prerequisites

- Kubernetes cluster (1.20+)
- kubectl configured
- Container registry access

### Step 1: Build and Push Images

```bash
# Tag images for your registry
docker tag whisper-api:latest your-registry.com/whisper-api:latest
docker tag whisper-api-gpu:latest your-registry.com/whisper-api-gpu:latest

# Push to registry
docker push your-registry.com/whisper-api:latest
docker push your-registry.com/whisper-api-gpu:latest
```

### Step 2: Update Configuration

Edit `k8s-deployment.yml` and update image references:

```yaml
image: your-registry.com/whisper-api:latest
```

### Step 3: Deploy to Kubernetes

```bash
# Create namespace and deploy
kubectl apply -f k8s-deployment.yml

# Deploy GPU variant (if you have GPU nodes)
kubectl apply -f k8s-deployment-gpu.yml

# Setup ingress
kubectl apply -f k8s-ingress.yml

# Check deployment status
kubectl get pods -n whisper-speech-recognition
kubectl get services -n whisper-speech-recognition
```

### Step 4: Configure Secrets

```bash
# Create secrets
kubectl create secret generic whisper-secrets \
  --from-literal=WANDB_API_KEY=your_key \
  --from-literal=HF_TOKEN=your_token \
  -n whisper-speech-recognition
```

### Step 5: Access the Service

```bash
# Get external IP
kubectl get service whisper-api-cpu-service -n whisper-speech-recognition

# Port forward for testing
kubectl port-forward service/whisper-api-cpu-service 8000:80 -n whisper-speech-recognition
```

### Scaling

```bash
# Scale manually
kubectl scale deployment whisper-api-cpu --replicas=5 -n whisper-speech-recognition

# Enable autoscaling (already configured in deployment)
kubectl get hpa -n whisper-speech-recognition
```

---

## AWS Deployment

### Option 1: AWS ECS (Elastic Container Service)

#### Prerequisites

- AWS CLI configured
- ECR repository created

#### Build and Push to ECR

```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com

# Tag and push
docker tag whisper-api:latest YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/whisper-api:latest
docker push YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/whisper-api:latest
```

#### Create ECS Task Definition

```json
{
  "family": "whisper-api",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "2048",
  "memory": "4096",
  "containerDefinitions": [
    {
      "name": "whisper-api",
      "image": "YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/whisper-api:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "TARGET_LANGUAGE",
          "value": "es"
        }
      ],
      "secrets": [
        {
          "name": "WANDB_API_KEY",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:ACCOUNT:secret:whisper-secrets-XXXXX:WANDB_API_KEY::"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/whisper-api",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

#### Create ECS Service

```bash
# Create service
aws ecs create-service \
  --cluster your-cluster \
  --service-name whisper-api-service \
  --task-definition whisper-api \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx],assignPublicIp=ENABLED}" \
  --load-balancers "targetGroupArn=arn:aws:elasticloadbalancing:...,containerName=whisper-api,containerPort=8000"
```

### Option 2: AWS EKS (Elastic Kubernetes Service)

```bash
# Create EKS cluster
eksctl create cluster \
  --name whisper-cluster \
  --region us-east-1 \
  --nodegroup-name standard-workers \
  --node-type t3.large \
  --nodes 3 \
  --nodes-min 2 \
  --nodes-max 5 \
  --managed

# Deploy application
kubectl apply -f k8s-deployment.yml
```

### Option 3: AWS Lambda (Serverless)

For lightweight deployments with less frequent use:

```python
# lambda_function.py
import json
import base64
from whisper_client import WhisperClient

def lambda_handler(event, context):
    # Get audio from event
    audio_data = base64.b64decode(event['body'])
    
    # Process with Whisper
    client = WhisperClient()
    result = client.transcribe(audio_data)
    
    return {
        'statusCode': 200,
        'body': json.dumps(result)
    }
```

---

## Google Cloud Platform

### Option 1: Google Cloud Run

#### Build and Deploy

```bash
# Build with Cloud Build
gcloud builds submit --tag gcr.io/PROJECT_ID/whisper-api

# Deploy to Cloud Run
gcloud run deploy whisper-api \
  --image gcr.io/PROJECT_ID/whisper-api \
  --platform managed \
  --region us-central1 \
  --memory 4Gi \
  --cpu 2 \
  --timeout 300 \
  --set-env-vars TARGET_LANGUAGE=es \
  --allow-unauthenticated
```

#### With GPU (requires Compute Engine)

```bash
# Create VM with GPU
gcloud compute instances create whisper-gpu-instance \
  --zone=us-central1-a \
  --machine-type=n1-standard-4 \
  --accelerator=type=nvidia-tesla-t4,count=1 \
  --image-family=pytorch-latest-gpu \
  --image-project=deeplearning-platform-release \
  --boot-disk-size=100GB \
  --metadata-from-file startup-script=startup.sh
```

### Option 2: Google Kubernetes Engine (GKE)

```bash
# Create GKE cluster
gcloud container clusters create whisper-cluster \
  --zone us-central1-a \
  --num-nodes 3 \
  --machine-type n1-standard-4 \
  --enable-autoscaling \
  --min-nodes 2 \
  --max-nodes 10

# Get credentials
gcloud container clusters get-credentials whisper-cluster --zone us-central1-a

# Deploy application
kubectl apply -f k8s-deployment.yml
```

---

## Azure Deployment

### Option 1: Azure Container Instances

```bash
# Create resource group
az group create --name whisper-rg --location eastus

# Create container instance
az container create \
  --resource-group whisper-rg \
  --name whisper-api \
  --image your-registry.azurecr.io/whisper-api:latest \
  --cpu 2 \
  --memory 4 \
  --ports 8000 \
  --dns-name-label whisper-api-unique \
  --environment-variables TARGET_LANGUAGE=es \
  --secure-environment-variables WANDB_API_KEY=your_key
```

### Option 2: Azure Kubernetes Service (AKS)

```bash
# Create AKS cluster
az aks create \
  --resource-group whisper-rg \
  --name whisper-aks-cluster \
  --node-count 3 \
  --node-vm-size Standard_DS3_v2 \
  --enable-managed-identity \
  --generate-ssh-keys

# Get credentials
az aks get-credentials --resource-group whisper-rg --name whisper-aks-cluster

# Deploy application
kubectl apply -f k8s-deployment.yml
```

### Option 3: Azure App Service

```bash
# Create App Service plan
az appservice plan create \
  --name whisper-plan \
  --resource-group whisper-rg \
  --sku P1V2 \
  --is-linux

# Create web app
az webapp create \
  --resource-group whisper-rg \
  --plan whisper-plan \
  --name whisper-api-app \
  --deployment-container-image-name your-registry.azurecr.io/whisper-api:latest
```

---

## DigitalOcean Deployment

### Option 1: DigitalOcean App Platform

```yaml
# .do/app.yaml
name: whisper-api
services:
- name: api
  image:
    registry_type: DOCKER_HUB
    repository: your-username/whisper-api
    tag: latest
  instance_count: 2
  instance_size_slug: professional-m
  http_port: 8000
  routes:
  - path: /
  envs:
  - key: TARGET_LANGUAGE
    value: "es"
  - key: WANDB_API_KEY
    value: ${WANDB_API_KEY}
    type: SECRET
```

Deploy:

```bash
doctl apps create --spec .do/app.yaml
```

### Option 2: DigitalOcean Kubernetes

```bash
# Create Kubernetes cluster
doctl kubernetes cluster create whisper-cluster \
  --region nyc1 \
  --node-pool "name=worker-pool;size=s-4vcpu-8gb;count=3"

# Get credentials
doctl kubernetes cluster kubeconfig save whisper-cluster

# Deploy application
kubectl apply -f k8s-deployment.yml
```

---

## Monitoring and Logging

### Prometheus + Grafana

```yaml
# Add to your deployment
- name: metrics
  port: 9090
  targetPort: 9090
```

### Application Logs

```bash
# Kubernetes logs
kubectl logs -f deployment/whisper-api-cpu -n whisper-speech-recognition

# Docker logs
docker-compose logs -f whisper-api-cpu
```

### Health Monitoring

```bash
# Setup monitoring endpoint
curl http://your-api-url/health

# Response
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00",
  "gpu_available": true,
  "model_loaded": true
}
```

---

## Performance Optimization

### 1. Load Balancing

Configure load balancer for multiple instances:

```yaml
# Kubernetes
apiVersion: v1
kind: Service
metadata:
  name: whisper-api-lb
spec:
  type: LoadBalancer
  selector:
    app: whisper-api
  ports:
  - port: 80
    targetPort: 8000
```

### 2. Caching

Implement Redis caching for repeated requests:

```python
import redis

redis_client = redis.Redis(host='localhost', port=6379)

def get_cached_transcription(audio_hash):
    return redis_client.get(f"transcription:{audio_hash}")

def cache_transcription(audio_hash, result):
    redis_client.setex(f"transcription:{audio_hash}", 3600, result)
```

### 3. Auto-scaling

Configure based on CPU/Memory metrics:

```yaml
# Already configured in k8s-deployment-gpu.yml
spec:
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        averageUtilization: 70
```

---

## Security Best Practices

### 1. HTTPS/TLS

Always use HTTPS in production:

```yaml
# k8s-ingress.yml
spec:
  tls:
  - hosts:
    - whisper-api.example.com
    secretName: whisper-api-tls
```

### 2. Authentication

Implement API key authentication:

```python
from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key")

async def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != os.getenv("API_KEY"):
        raise HTTPException(status_code=403, detail="Invalid API key")
    return api_key
```

### 3. Rate Limiting

Implement rate limiting:

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/transcribe")
@limiter.limit("10/minute")
async def transcribe(request: Request):
    # ... implementation
```

---

## Cost Optimization

### 1. Use Spot Instances

AWS:
```bash
--capacity-provider-strategy capacityProvider=FARGATE_SPOT,weight=1
```

GCP:
```bash
--preemptible
```

### 2. Auto-shutdown

Schedule non-production environments:

```bash
# Shutdown at night
0 22 * * * kubectl scale deployment whisper-api-cpu --replicas=0
0 6 * * * kubectl scale deployment whisper-api-cpu --replicas=2
```

### 3. Model Optimization

- Use quantized models
- Implement model caching
- Batch processing when possible

---

## Troubleshooting

### Common Issues

1. **Out of Memory**
   - Increase memory limits
   - Use CPU instead of GPU
   - Process smaller audio chunks

2. **Slow Response Times**
   - Enable GPU acceleration
   - Increase replicas
   - Optimize model loading

3. **Connection Timeouts**
   - Increase timeout values
   - Check network configuration
   - Verify firewall rules

---

## Support

For deployment assistance:
- Documentation: See project README
- GitHub Issues: [Project Repository]
- Email: support@example.com

---

**Happy Deploying! 🚀**
