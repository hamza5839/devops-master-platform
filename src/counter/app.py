import os, socket, json, time
from flask import Flask, jsonify
import redis
from prometheus_flask_exporter import PrometheusMetrics

app = Flask(__name__)
metrics = PrometheusMetrics(app)

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PASS = os.getenv("REDIS_PASSWORD", None)
LOG_PATH = os.getenv("LOG_PATH", "/tmp/audit.log")
FAIL_MODE = False

cache = redis.Redis(host=REDIS_HOST, port=6379, password=REDIS_PASS, decode_responses=True)

@app.route("/healthz")
def healthz():
    return jsonify(status="alive", pod=socket.gethostname()), 200 if not FAIL_MODE else 500

@app.route("/readyz")
def readyz():
    try:
        cache.ping()
        return jsonify(status="ready"), 200
    except Exception as e:
        return jsonify(status="not_ready", error=str(e)), 503

@app.route("/toggle-fail", methods=["POST"])
def toggle_fail():
    global FAIL_MODE
    FAIL_MODE = not FAIL_MODE
    return jsonify(fail_mode=FAIL_MODE, pod=socket.gethostname()), 200

@app.route("/count")
def count():
    visits = cache.incr("hits")
    log_entry = json.dumps({"ts": time.time(), "service": "counter", "pod": socket.gethostname(), "hits": visits})
    print(log_entry, flush=True)
    with open(LOG_PATH, "a") as f:
        f.write(log_entry + "\n")
    return jsonify(service="counter", hits=visits, pod=socket.gethostname()), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)