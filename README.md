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

# 3. Install MySQL Operator CRDs and controller
kubectl apply -f kubernetes/mysql-operator-crds.yaml
kubectl apply -f kubernetes/mysql-operator.yaml
kubectl -n mysql-operator wait --for=condition=Available deployment/mysql-operator --timeout=180s

# 4. Apply MySQL manifests
kubectl apply -f kubernetes/mysql/secret.yaml
kubectl apply -f kubernetes/mysql/backup.yaml
kubectl apply -f kubernetes/mysql/innodb-cluster.yaml
kubectl wait --for=jsonpath='{.status.cluster.status}'=ONLINE innodbcluster/livemech-mysql --timeout=180s
kubectl apply -f kubernetes/mysql/create-db-job.yaml
kubectl wait --for=condition=complete job/livemech-create-db --timeout=60s

# 5. Apply app manifests
kubectl apply -f kubernetes/deployment.yaml
kubectl apply -f kubernetes/service.yaml
kubectl apply -f kubernetes/ingress.yaml

# 6. Watch rollout (init container runs migrations before pods start)
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

# Check InnoDB Cluster status
kubectl get innodbcluster livemech-mysql

# View app logs
kubectl logs -l app=livemech

# View migration logs (init container)
kubectl logs <pod-name> -c run-migrations

# Restart all app pods
kubectl rollout restart deployment/livemech

# List backups
kubectl get mysqlbackup

# Trigger a manual backup
kubectl apply -f - <<EOF
apiVersion: mysql.oracle.com/v2
kind: MySQLBackup
metadata:
  name: livemech-backup-manual
spec:
  clusterName: livemech-mysql
  backupProfile:
    dumpInstance:
      storage:
        persistentVolumeClaim:
          claimName: mysql-backup-pvc
EOF
```

### MySQL services created by the operator

| Service | Purpose |
|---|---|
| `livemech-mysql` | Read/write (primary) — used by the app |
| `livemech-mysql-ro` | Read-only (replicas, when instances > 1) |
| `livemech-mysql-instances` | Direct pod access |

### Connecting with MySQL Workbench

MySQL is inside the cluster — use port-forward to expose it locally:

```bash
# Primary (read/write)
kubectl port-forward svc/livemech-mysql 3306:3306

# Read-only replicas (when instances > 1)
kubectl port-forward svc/livemech-mysql-ro 3307:3306
```

Then connect Workbench to:

| | Primary | Read-only |
|---|---|---|
| Host | `127.0.0.1` | `127.0.0.1` |
| Port | `3306` | `3307` |
| Username | `root` | `root` |
| Password | `Password47` | `Password47` |

Keep the port-forward terminal open while using Workbench. The router automatically routes to the current primary — no changes needed if a failover occurs.

### Scaling

**MySQL (InnoDB Cluster)** — edit `instances` in `kubernetes/mysql/innodb-cluster.yaml`:

```yaml
instances: 3    # must be odd: 1, 3, 5...
router:
  instances: 2  # scale routers independently
```

```bash
kubectl apply -f kubernetes/mysql/innodb-cluster.yaml
kubectl get innodbcluster livemech-mysql --watch
```

The operator handles replication and primary election automatically.

> **Note:** Always use an odd number of MySQL instances (1, 3, 5) for group replication quorum. Never use 2 or 4.

**App (livemech)** — edit `replicas` in `kubernetes/deployment.yaml`, then apply:

```bash
kubectl apply -f kubernetes/deployment.yaml

# Or imperatively
kubectl scale deployment/livemech --replicas=3
```

---

> **Note:** Do not commit `kubernetes/mysql/secret.yaml` with real credentials.
> Use `kubectl create secret` or a secrets manager in production.
