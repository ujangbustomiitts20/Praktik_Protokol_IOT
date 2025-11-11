import os, logging, time
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import psutil

load_dotenv()
HOST = os.getenv("HTTP_HOST","127.0.0.1")
PORT = int(os.getenv("HTTP_PORT","5000"))

app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [HTTP-SRV] %(levelname)s: %(message)s")

counter = 0

@app.route("/ingest", methods=["POST"])
def ingest():
    global counter
    data = request.get_json(force=True, silent=True) or {}
    counter += 1
    return jsonify({"ok": True, "counter": counter}), 200

@app.route("/metrics", methods=["GET"])
def metrics():
    cpu = psutil.Process().cpu_percent(interval=0.1)
    return jsonify({"requests": counter, "cpu_percent": cpu})

if __name__ == "__main__":
    app.run(host=HOST, port=PORT)
