# 🚀 DevOps Master Platform — Cloud-Native Microservices, DevSecOps & Helm Architecture

An enterprise-grade, observable, and security-hardened 3-tier microservices platform engineered with end-to-end Shift-Left DevSecOps practices, multi-stage container optimization, zero-trust Kubernetes Calico microsegmentation, and dynamic multi-environment Helm packaging.

---

## 🗺️ Repository Structure

```text
devops-master-platform/
├── .github/workflows/          # Shift-Left DevSecOps CI Pipeline (Gitleaks, Hadolint, Trivy)
├── charts/
│   └── devops-platform/        # Phase 4: Dynamic Multi-Environment Helm Chart
│       ├── Chart.yaml          # Chart metadata (v1.0.0, appVersion 3.0.0)
│       ├── values.yaml         # Development environment defaults (devops-dev)
│       ├── values-prod.yaml    # Production environment overrides (devops-platform)
│       └── templates/          # Parameterized Kubernetes & Calico YAML blueprints
├── k8s/                        # Phase 3: Static Kubernetes & Calico CNI Manifests
│   ├── kind-config.yaml        # 3-Node Kind Cluster topology & NodePort host mapping
│   ├── 00-namespace-config.yaml# Restricted PSA Namespace, ConfigMap, and Secret
│   ├── 01-redis.yaml           # StatefulSet, Headless Service, and 1Gi PVC
│   ├── 02-counter.yaml         # Backend Flask Deployment & ClusterIP Service
│   ├── 03-gateway.yaml         # Frontend Gateway Deployment & NodePort Service
│   └── 04-network-policy.yaml  # 7-Rule Calico Zero-Trust NetworkPolicies
├── services/                   # Phase 1: Application Source & Hardened Dockerfiles
│   ├── gateway-service/        # Frontend UI, Prometheus metrics, and chaos endpoints
│   └── counter-service/        # Backend state manager interfacing with Redis
├── docker-compose.yml          # Local 3-tier hardened container orchestration
└── README.md                   # Architecture & engineering documentation
```

---

## 🏗️ Phase 1: Local Foundation & Runtime Hardening (`v1.0-phase1-docker`)

### Purpose
Build an unprivileged, immutable, and observable 3-tier microservices stack (`gateway-service`, `counter-service`, and `redis-db`) running locally on Docker Compose with strict kernel and filesystem isolation.

### Architecture & Data Flow
```text
[ Browser / Client ] 
         │ (HTTP :5000)
         ▼
┌─────────────────────────┐
│     gateway-service     │  (Flask + Gunicorn | UID 10001 | Read-Only Root | Tmpfs RAM-Disk)
└─────────────────────────┘
         │ (Internal Docker DNS: http://counter-service:5001)
         ▼
┌─────────────────────────┐
│     counter-service     │  (Flask + Gunicorn | UID 10001 | Read-Only Root | Tmpfs RAM-Disk)
└─────────────────────────┘
         │ (TCP :6379 | Password Authenticated)
         ▼
┌─────────────────────────┐
│      redis-db (7.2)     │  (Stateful Persistence via Docker Volume: redis-data)
└─────────────────────────┘
```

### Key Engineering Highlights
- **Multi-Stage Container Optimization:** Separated build-time compilers (`builder`) from lightweight runtime environments (`runner`) on `python:3.11-slim`, achieving a **97% image efficiency score** verified via `dive`.
- **OverlayFS Layer Deduplication:** Implemented `COPY --chown=10001:10001` during stage transfers to eliminate Copy-on-Write (CoW) metadata duplication across image layers.
- **Zero-Trust Runtime Hardening:** Enforced `read_only: true` root filesystems and `cap_drop: [ALL]` kernel capability stripping across all application containers, paired with in-memory `tmpfs` RAM-disks mounted at `/tmp`.
- **Built-In Observability & Chaos Endpoints:**
  - **Live Telemetry UI (`/`):** Real-time dark-mode dashboard polling container hostnames, global Redis hit state, probe health, and structured JSON logs.
  - **Prometheus Metrics (`/metrics`):** Exposes HTTP request latencies and process telemetry.
  - **Kubernetes-Ready Probes (`/healthz` & `/readyz`):** Liveness check and deep upstream dependency verification.
  - **Chaos Engineering (`/stress` & `/toggle-fail`):** On-demand CPU saturation and failure injection for testing resilience.

---

## 🛡️ Phase 2: Shift-Left DevSecOps CI Pipeline (`v2.0-phase2-cicd`)

### Purpose
Automate security validation directly into the Git workflow via GitHub Actions so that exposed secrets, Dockerfile anti-patterns, or critical container CVEs block the pipeline before merge.

### Pipeline Architecture
```text
[ Developer Git Push ] ──► [ GitHub Actions CI Trigger ]
                                 │
         ┌───────────────────────┼───────────────────────┐
         ▼                       ▼                       ▼
  ┌──────────────┐        ┌──────────────┐        ┌──────────────┐
  │   Gitleaks   │        │   Hadolint   │        │ Trivy Config │
  │(Secret Scan) │        │(Dockerfile)  │        │(YAML Checks) │
  └──────────────┘        └──────────────┘        └──────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 ▼
                        ┌──────────────┐
                        │ Docker Build │
                        │  (BuildKit)  │
                        └──────────────┘
                                 ▼
                        ┌──────────────┐
                        │  Trivy Scan  │
                        │ (CVE Check)  │
                        └──────────────┘
                                 ▼
                        [ Pipeline Success ✅ ]
```

### Key Engineering Highlights
- **Secret Leak Detection (Gitleaks):** Scans full repository commit histories on every push to prevent accidental credential exposure.
- **Static Dockerfile Linting (Hadolint):** Enforces pinned package versions, proper layer caching, and non-root execution directives.
- **Automated CVE Gatekeeping (Trivy):** Scans both static Kubernetes/Compose manifests and compiled container images for `HIGH` and `CRITICAL` vulnerabilities.

---

## ☸️ Phase 3: Kubernetes Orchestration, Pod Security & Zero-Trust Networking (`v3.0-phase3-k8s`)

### Purpose
Transition the 3-tier platform onto a multi-node Kubernetes cluster enforcing Kubernetes Pod Security Admission (`restricted`) and Layer 3/4 zero-trust microsegmentation via Calico CNI.

### Cluster & Zero-Trust Network Topology
```text
[ Host Machine :5000 ] ──► [ Kind Worker NodePort :30080 ]
                                       │
   ┌───────────────────────────────────┴───────────────────────────────────┐
   │ Namespace: devops-platform (PSA Enforce: restricted | Default-Deny)   │
   │                                                                       │
   │  ┌──────────────────────┐                                             │
   │  │   gateway-service    │  (2 Replicas | UID 10001 | Read-Only Root)  │
   │  └──────────┬───────────┘                                             │
   │             │ ALLOWED: TCP :5001 (Calico NetworkPolicy)               │
   │             ▼                                                         │
   │  ┌──────────────────────┐                                             │
   │  │   counter-service    │  (2 Replicas | UID 10001 | ClusterIP)       │
   │  └──────────┬───────────┘                                             │
   │             │ ALLOWED: TCP :6379 (Calico NetworkPolicy)               │
   │             ▼                                                         │
   │  ┌──────────────────────┐                                             │
   │  │   redis-0 (Stateful) │  (1 Replica  | UID 999   | 1Gi PVC AOF)     │
   │  └──────────────────────┘                                             │
   └───────────────────────────────────────────────────────────────────────┘
         ▲               ▲
         └───┴───────────────┴─── ALLOWED: UDP/TCP :53 to kube-dns ONLY
```

### Key Engineering Highlights
1. **Multi-Node Cluster & CNI (`k8s/kind-config.yaml`):**
   - Deployed a 3-node Kind cluster (`1` Control Plane + `2` Worker Nodes) running Kubernetes `v1.32.2`.
   - Disabled default `kindnet` (`disableDefaultCNI: true`) and installed **Calico CNI (`v3.29.2`)** over custom Pod CIDR `192.168.0.0/16` to enforce strict network policy rules.
2. **Namespace Security & Decoupled Config (`k8s/00-namespace-config.yaml`):**
   - Enforced `pod-security.kubernetes.io/enforce: restricted` across the namespace.
   - Externalized non-sensitive settings into `platform-config` (`ConfigMap`) and Redis credentials into `redis-secret` (`Secret`).
3. **Stateful & Stateless Workloads (`01-redis.yaml`, `02-counter.yaml`, `03-gateway.yaml`):**
   - **Database Tier (`StatefulSet`):** Deployed `redis-0` with a Headless Service (`clusterIP: None`) and a `1Gi` `PersistentVolumeClaim` (`local-path-storage`) configured with `--appendonly yes` AOF persistence.
   - **App Tiers (`Deployment`):** Deployed 2 replicas each of `counter-service` (`ClusterIP:5001`) and `gateway-service` (`NodePort:30080`) with non-root UIDs, `readOnlyRootFilesystem: true`, `RuntimeDefault` seccomp profiles, dropped Linux capabilities (`ALL`), and in-memory `emptyDir` `/tmp` volumes.
4. **Zero-Trust Microsegmentation (`k8s/04-network-policy.yaml`):**
   - Implemented a **7-rule Calico NetworkPolicy architecture**: global default-deny for all ingress/egress traffic, explicit DNS egress allowance (`UDP/TCP 53` to `kube-system`), and strict least-privilege service chaining (`gateway` ➔ `counter:5001` ➔ `redis:6379`).

---

## 📦 Phase 4: Helm Packaging & Multi-Environment Configuration (`v4.0-phase4-helm`)

### Purpose
Eliminate static YAML duplication by converting the Kubernetes manifests into a reusable, parameterized **Helm Chart (`devops-platform`)** capable of deploying isolated `dev` and `prod` environments side-by-side on the same cluster.

### Multi-Environment Helm Architecture
```text
                   ┌──────────────────────────────────────┐
                   │   Helm Chart: charts/devops-platform │
                   │     (Templates + Go Variables)       │
                   └──────────────────┬───────────────────┘
                                      │
              ┌───────────────────────┴───────────────────────┐
              ▼ (-f values.yaml)                              ▼ (-f values-prod.yaml)
┌───────────────────────────────┐               ┌───────────────────────────────┐
│   Release: dev-stack          │               │   Release: prod-stack         │
│   Namespace: devops-dev       │               │   Namespace: devops-platform  │
├───────────────────────────────┤               ├───────────────────────────────┤
│ • Replicas: 1 per service     │               │ • Replicas: 2 per service (HA)│
│ • NodePort: 30081             │               │ • NodePort: 30080 (:5000)     │
│ • CPU/RAM: 30m / 32Mi         │               │ • CPU/RAM: 50m / 64Mi         │
│ • Isolated Calico Policies    │               │ • Isolated Calico Policies    │
└───────────────────────────────┘               └───────────────────────────────┘
```

### Key Engineering Highlights
- **DRY Template Parameterization (`templates/`):** Replaced hardcoded namespaces, replica counts, resource limits, and service ports with dynamic Go template expressions (`{{ .Values... }}`).
- **Dynamic Zero-Trust Policy Binding:** Parameterized all 7 Calico `NetworkPolicy` manifests inside `templates/04-network-policy.yaml` so microsegmentation rules automatically scope to `{{ .Values.namespace }}` upon installation.
- **Release Lifecycle & Verification:**
  - Validated syntax and best practices using `helm lint ./charts/devops-platform`.
  - Audited rendered manifests offline using `helm template` dry-runs prior to cluster apply.
  - Managed live multi-revision upgrades (`helm upgrade`) and verified revision history stored in Kubernetes encrypted release Secrets (`sh.helm.release.v1.*`).

---

## ⚡ Quick Start & Verification Commands

### 1. Local Docker Compose (Phase 1)
```bash
git clone git@github.com:hamza5839/devops-master-platform.git
cd devops-master-platform
docker compose up -d --build
docker compose ps
curl -i http://localhost:5000/healthz
curl -i http://localhost:5000/readyz
```

### 2. Multi-Environment Helm Deployment (Phase 4)
```bash
# Lint & Dry-Run Render
helm lint ./charts/devops-platform
helm template dev-stack ./charts/devops-platform

# Deploy Development Environment (Namespace: devops-dev | NodePort: 30081)
helm install dev-stack ./charts/devops-platform --create-namespace

# Deploy Production Environment (Namespace: devops-platform | NodePort: 30080)
helm install prod-stack ./charts/devops-platform -f ./charts/devops-platform/values-prod.yaml --create-namespace

# Verify Releases & Pods Across Environments
helm list -A
kubectl get pods -n devops-dev
kubectl get pods -n devops-platform
curl -s http://localhost:5000/healthz
```

---

## 🔖 Release Milestones
- **`v1.0-phase1-docker`**: 3-tier microservices foundation, hardened multi-stage Dockerfiles, Compose orchestration, and real-time observability UI.
- **`v2.0-phase2-cicd`**: Automated DevSecOps GitHub Actions pipeline with Gitleaks, Hadolint, and Trivy vulnerability scanning.
- **`v3.0-phase3-k8s`**: 3-node Kind cluster, Calico CNI, Restricted Pod Security Standards, StatefulSet persistence, and 7-rule zero-trust microsegmentation.
- **`v4.0-phase4-helm`**: Parameterized Helm chart supporting side-by-side isolated `dev` and `prod` multi-environment deployments.

---
