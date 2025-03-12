
from argparse import ArgumentParser

# parse argument
argparser = ArgumentParser("Run phishing detector Flask API")
argparser.add_argument('--port', default=5000, type=int,
                       help="port number (default: 5000)")
args = argparser.parse_args()


import os

from flask import Flask, request, jsonify
import numpy as np
import onnxruntime
from huggingface_hub import hf_hub_download
from dotenv import load_dotenv

load_dotenv()

# Downloading / Loading the model
REPO_ID = os.getenv("PHISHING_REPO_ID")
FILENAME = os.getenv("PHISHING_FILE_ID")
model_path = hf_hub_download(repo_id=REPO_ID, filename=FILENAME)

# Initializing the ONNX Runtime session with the pre-trained model
sess = onnxruntime.InferenceSession(
    model_path,
    providers=["CPUExecutionProvider"],
)

# Starting the Flask API
app = Flask("Phishingdetector")


@app.route("/", methods=['GET'])
def hello():
    data = request.get_json(force=True)
    name = data.get("name", "Amigo")
    return jsonify({"message": "Hello, {}!".format(name)})


@app.route("/detectphishing", methods=['GET'])
def detect_phishing():
    data = request.get_json(force=True)
    url = data.get('url')
    if url is None:
        return jsonify({
            "query": data,
            "message": "URL is not provided!"
        })

    results = sess.run(None, {"inputs": [url]})
    return jsonify({
        "query": data,
        "result": {
            "url": url,
            "phishing": (results[0][0] == 1),
            "phishing_probability": float(results[1][0, 1])
        }
    })


if __name__ == "__main__":
    app.run(port=args.port)
