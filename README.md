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
