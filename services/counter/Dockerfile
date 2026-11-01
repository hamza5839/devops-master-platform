FROM python:3.11-slim AS builder
WORKDIR /build
COPY requirements.txt .
RUN pip install --no-cache-dir --default-timeout=100 --retries 10 --user -r requirements.txt

FROM python:3.11-slim AS runner
WORKDIR /app
RUN groupadd -g 10001 appgroup && \
    useradd -u 10001 -g appgroup -s /bin/sh -M appuser
COPY --from=builder --chown=10001:10001 /root/.local /home/appuser/.local
COPY --chown=10001:10001 app.py .
ENV PATH=/home/appuser/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1
USER 10001:10001
EXPOSE 5001
CMD ["gunicorn", "--bind", "0.0.0.0:5001", "--workers", "2", "--timeout", "30", "app:app"]
