from flask import Flask, request, jsonify
import threading
import subprocess
import os

app = Flask(__name__)
RESULT_FILE = "/workspace/shared_data/results/pyats_results.json"


def run_pyats():
    os.makedirs(os.path.dirname(RESULT_FILE), exist_ok=True)
    subprocess.run(["python", "/workspace/workflow/pyats_test.py"])


@app.route("/run-tests", methods=["POST"])
def run_tests():
    t = threading.Thread(target=run_pyats)
    t.start()
    return jsonify({"status": "started"}), 202


if __name__ == "__main__":
    host = os.environ.get("PYATS_HOST", "0.0.0.0")
    port = int(os.environ.get("PYATS_PORT", 5000))
    app.run(host=host, port=port)
