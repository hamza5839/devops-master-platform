import os, socket, time, math, json
import requests
from flask import Flask, jsonify, render_template
from prometheus_flask_exporter import PrometheusMetrics

app = Flask(__name__)
metrics = PrometheusMetrics(app)

COUNTER_URL = os.getenv("COUNTER_URL", "http://localhost:5001/count")
APP_ENV = os.getenv("APP_ENV", "local-dev")

@app.route("/")
def index():
    return render_template("index.html", env=APP_ENV)

@app.route("/healthz")
def healthz():
    return jsonify(status="alive", env=APP_ENV, pod=socket.gethostname()), 200

@app.route("/readyz")
def readyz():
    try:
        r = requests.get("http://counter-service:5001/healthz", timeout=1)
        return jsonify(status="ready", upstream=r.status_code), 200 if r.status_code == 200 else 503
    except Exception as e:
        return jsonify(status="not_ready", error=str(e)), 503

@app.route("/stress")
def stress():
    end = time.time() + 3
    while time.time() < end:
        math.sqrt(123456789)
    return jsonify(status="cpu_stressed_for_3s", pod=socket.gethostname()), 200

@app.route("/api")
def api():
    resp = requests.get(COUNTER_URL, timeout=2).json()
    print(json.dumps({"ts": time.time(), "service": "gateway", "env": APP_ENV, "pod": socket.gethostname()}), flush=True)
    return jsonify(env=APP_ENV, gateway_pod=socket.gethostname(), upstream=resp), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

    #dummy eidt here.