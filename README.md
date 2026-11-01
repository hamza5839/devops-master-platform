# 🚀 DevOps Master Platform — 3-Tier Cloud-Native Microservices

An enterprise-grade, observable, and security-hardened 3-tier microservices platform engineered to demonstrate end-to-end DevSecOps practices—from multi-stage container optimization and zero-trust runtime hardening to automated CI/CD pipelines and Kubernetes orchestration.

---

## 🏗️ System Architecture (Phase 1: Local Foundation)

```text
[ Browser / Client ] 
         │ (HTTP :5000)
         ▼
┌─────────────────────────┐
│     gateway-service     │  (Flask + Gunicorn | UID 10001 | Tailwind Telemetry UI)
└─────────────────────────┘
         │ (Internal Docker DNS: http://counter-service:5001)
         ▼
┌─────────────────────────┐
│     counter-service     │  (Flask + Gunicorn | UID 10001 | JSON Audit Logger)
└─────────────────────────┘
         │ (TCP :6379 | Password Authenticated)
         ▼
┌─────────────────────────┐
│      redis-db (7.2)     │  (Stateful Persistence via Docker Volume: redis-data)
└─────────────────────────┘
Core Engineering Highlights
Multi-Stage Container Optimization: Separated build-time compilers (builder) from lightweight runtime environments (runner) on python:3.11-slim, achieving a 97% image efficiency score verified via dive.

OverlayFS Layer Deduplication: Implemented COPY --chown=10001:10001 during stage transfers to avoid Copy-on-Write (CoW) metadata duplication across layers.

Principle of Least Privilege: Stripped root access across all application containers, executing Gunicorn workers strictly under unprivileged UID/GID 10001:10001.

PID 1 Signal Handling: Configured Exec-form entrypoints (CMD ["gunicorn", ...]) to ensure gunicorn runs as PID 1 and handles SIGTERM for graceful shutdowns.

Race-Condition Free Orchestration: Enforced startup ordering in Docker Compose using active redis-cli ping health probes (condition: service_healthy).

Built-In Observability & Chaos Endpoints:

Live Telemetry UI (/): Real-time dark-mode dashboard polling container hostnames, global Redis hit state, probe health, and structured JSON logs.

Prometheus Metrics (/metrics): Exposes HTTP request latencies, status codes, and process telemetry via prometheus-flask-exporter.

Kubernetes-Ready Probes (/healthz & /readyz): Liveness check and deep upstream dependency readiness verification.

Chaos Engineering (/stress & /toggle-fail): On-demand CPU saturation and failure injection endpoints for testing autoscaling and self-healing.
