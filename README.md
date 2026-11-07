# 🚀 DevOps Master Platform — 3-Tier Cloud-Native Microservices & DevSecOps CI/CD

An enterprise-grade, observable, and security-hardened 3-tier microservices platform engineered with end-to-end Shift-Left DevSecOps practices—featuring multi-stage container optimization, zero-trust runtime immutability, automated security linting, secret leak detection, and container vulnerability scanning via GitHub Actions.

---

## 🏗️ System Architecture & Workflow

### Phase 1: Local Foundation & Runtime Hardening
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

### Phase 2: Shift-Left DevSecOps CI Pipeline
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
                        │ (BuildKit)   │
                        └──────────────┘
                                 ▼
                        ┌──────────────┐
                        │  Trivy Scan  │
                        │ (CVE Check)  │
                        └──────────────┘
                                 ▼
                        [ Pipeline Success ✅ ]
```

---

## 🛡️ Core Engineering & Security Highlights

* **Multi-Stage Container Optimization:** Separated build-time compilers (`builder`) from lightweight runtime environments (`runner`) on `python:3.11-slim`, achieving a **97% image efficiency score** verified via `dive`.
* **OverlayFS Layer Deduplication:** Implemented `COPY --chown=10001:10001` during stage transfers to avoid Copy-on-Write (CoW) metadata duplication across layers.
* **Zero-Trust Runtime Hardening:** Enforced `read_only: true` root filesystems and `cap_drop: [ALL]` kernel capability stripping across all application containers, paired with in-memory `tmpfs` RAM-disks at `/`tmp`.
* **Automated Shift-Left Security (CI/CD):** Integrated Gitleaks (secret detection), Hadolint (Dockerfile linting), and Trivy (container vulnerability scanning) into a fully automated GitHub Actions pipeline.
* **Built-In Observability & Chaos Endpoints:**
  * **Live Telemetry UI (`/`):** Real-time dark-mode dashboard polling container hostnames, global Redis hit state, probe health, and structured JSON logs.
  * **Prometheus Metrics (`/metrics`):** Exposes HTTP request latencies and process telemetry.
  * **Kubernetes-Ready Probes (`/healthz` & `/readyz`):** Liveness check and deep upstream dependency verification.
  * **Chaos Engineering (`/stress` & `/toggle-fail`):** On-demand CPU saturation and failure injection for testing resilience.

---

## ⚡ Quick Start (Local Docker Compose)

### 1. Clone & Launch the Stack
```bash
git clone git@github.com:hamza5839/devops-master-platform.git
cd devops-master-platform
docker compose up -d --build
```

### 2. Verify Services & Health Probes
```bash
docker compose ps
curl -i http://localhost:5000/healthz
curl -i http://localhost:5000/readyz
```

### 3. Access the Platform
* **Live Telemetry Dashboard:** `http://localhost:5000`
* **Gateway Prometheus Metrics:** `http://localhost:5000/metrics`
* **Counter Prometheus Metrics (Localhost Bound):** `http://localhost:5001/metrics`

---

## 🔖 Release Milestones
* **`v1.0-phase1-docker`**: Complete 3-tier microservices foundation, hardened multi-stage Dockerfiles, Compose orchestration, and real-time observability UI.
* **`v2.0-phase2-cicd`**: Automated DevSecOps GitHub Actions pipeline featuring Gitleaks secret detection, Hadolint static linting, and Trivy container vulnerability scanning.

---

## Phase 3: Kubernetes Orchestration, Pod Security & Zero-Trust Networking

### 1. Multi-Node Cluster & CNI Architecture (`k8s/kind-config.yaml`)
- **Topology:** 3-node Kind cluster (`1` Control Plane + `2` Worker Nodes) running Kubernetes `v1.32.2`.
- **CNI Plugin:** Disabled default `kindnet` (`disableDefaultCNI: true`) and deployed **Calico CNI (`v3.29.2`)** over custom Pod CIDR `192.168.0.0/16` to enforce Layer 3/4 NetworkPolicies.
- **Host Port Mapping:** Exposed Worker NodePort `30080` directly to host port `5000`.

### 2. Namespace Security & Configuration (`k8s/00-namespace-config.yaml`)
- **Pod Security Admission (PSA):** Enforced `pod-security.kubernetes.io/enforce: restricted` across the `devops-platform` namespace.
- **Decoupled Config & Secrets:** Externalized environment parameters into `platform-config` (`ConfigMap`) and database credentials into `redis-secret` (`Secret`).

### 3. Stateful & Stateless Workloads (`01-redis.yaml`, `02-counter.yaml`, `03-gateway.yaml`)
- **Database Tier (`StatefulSet`):** Deployed `redis-0` backed by a Headless Service (`clusterIP: None`) and a `1Gi` `PersistentVolumeClaim` (`local-path-storage`) with `--appendonly yes` AOF persistence.
- **Backend & Frontend Tiers (`Deployment`):** Deployed 2 replicas each of `counter-service` (`ClusterIP:5001`) and `gateway-service` (`NodePort:30080`), running as non-root UID `10001` (`999` for Redis), `readOnlyRootFilesystem: true`, `RuntimeDefault` seccomp profiles, dropped Linux capabilities (`ALL`), and in-memory `emptyDir` `/tmp` mounts.

### 4. Zero-Trust Microsegmentation (`k8s/04-network-policy.yaml`)
- **Default Deny & Least Privilege:** Enforced Calico `NetworkPolicy` rules isolating `redis` so it only accepts TCP `6379` traffic from `counter-service`, and `counter-service` only accepts TCP `5001` traffic from `gateway-service`.

## Phase 4: Helm Packaging & Multi-Environment Configuration

### 1. Chart Architecture & Blueprint Parameterization ()
- **Templating Engine:** Converted static manifests into a dynamic Helm chart structure (, , , and ) utilizing  variable injection.
- **Multi-Environment Strategy:** Maintained a single DRY chart codebase supporting side-by-side isolated deployments across  (,  replica, NodePort ) and  (,  replicas, NodePort ).

### 2. Zero-Trust NetworkPolicy & Release Management
- **Calico Microsegmentation Templates:** Parameterized all 7 core zero-trust Calico  blueprints () for dynamic namespace binding.
- **Lifecycle Commands:** Utilized ==> Linting .
Error unable to check Chart.yaml file in chart: stat Chart.yaml: no such file or directory,  dry-runs, , and  for seamless revision tracking and zero-downtime policy updates.

## Phase 4: Helm Packaging & Multi-Environment Configuration

### 1. Chart Architecture & Blueprint Parameterization (`charts/devops-platform/`)
- **Templating Engine:** Converted static manifests into a dynamic Helm chart structure (`Chart.yaml`, `values.yaml`, `values-prod.yaml`, and `templates/`) utilizing `{{ .Values... }}` variable injection.
- **Multi-Environment Strategy:** Maintained a single DRY chart codebase supporting side-by-side isolated deployments across `dev` (`devops-dev`, `1` replica, NodePort `30081`) and `prod` (`devops-platform`, `2` replicas, NodePort `30080`).

### 2. Zero-Trust NetworkPolicy & Release Management
- **Calico Microsegmentation Templates:** Parameterized all 7 core zero-trust Calico `NetworkPolicy` blueprints (`04-network-policy.yaml`) for dynamic namespace binding.
- **Lifecycle Commands:** Utilized `helm lint`, `helm template` dry-runs, `helm install --create-namespace`, and `helm upgrade` for seamless revision tracking and zero-downtime policy updates.
