# livemech

FastAPI service with MySQL, deployed on Kubernetes.

## Local development

```bash
uv sync
DATABASE_URL="mysql+asyncmy://root:Password47@localhost:3306/livemech" uv run uvicorn livemech.main:app --reload
```

Run migrations locally:

```bash
DATABASE_URL="mysql+asyncmy://root:Password47@localhost:3306/livemech" uv run alembic upgrade head
```

## Deploy to Kubernetes

### Prerequisites

- Docker
- `kubectl` connected to your cluster
- For local kind cluster: `kind` installed

### First-time setup

```bash
# 1. Create the kind cluster (if using kind)
kind create cluster --config kubernetes/cluster.yaml

# 2. Install nginx ingress controller
kubectl apply -f kubernetes/nginx-ingress.yaml
kubectl wait --namespace ingress-nginx \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/component=controller \
  --timeout=120s

# 3. Apply MySQL manifests
kubectl apply -f kubernetes/mysql/secret.yaml
kubectl apply -f kubernetes/mysql/service.yaml
kubectl apply -f kubernetes/mysql/statefulset.yaml
kubectl wait --for=condition=ready pod/mysql-0 --timeout=120s

# 4. Apply app manifests
kubectl apply -f kubernetes/deployment.yaml
kubectl apply -f kubernetes/service.yaml
kubectl apply -f kubernetes/ingress.yaml

# 5. Watch rollout (init container runs migrations before pods start)
kubectl rollout status deployment/livemech
```

### Deploying a new version

```bash
# 1. Build and push new image
docker build -t koskedk/livemech:0.0.2 .
docker push koskedk/livemech:0.0.2

# For kind (no registry): load image directly
kind load docker-image koskedk/livemech:0.0.2

# 2. Update image tag in kubernetes/deployment.yaml, then apply
kubectl apply -f kubernetes/deployment.yaml
kubectl rollout status deployment/livemech
```

### Useful commands

```bash
# Check pod status
kubectl get pods

# View app logs
kubectl logs -l app=livemech

# View migration logs (init container)
kubectl logs <pod-name> -c run-migrations

# Restart all app pods
kubectl rollout restart deployment/livemech
```

> **Note:** Do not commit `kubernetes/mysql/secret.yaml` with real credentials.
> Use `kubectl create secret` or a secrets manager in production.
