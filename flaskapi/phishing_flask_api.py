
from argparse import ArgumentParser

# parse argument
argparser = ArgumentParser("Run phishing detector Flask API")
argparser.add_argument('--port', default=5000, type=int,
                       help="port number (default: 5000)")
args = argparser.parse_args()


import os
from datetime import datetime, timezone
import json

from flask import Flask, request, jsonify
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


def write_log(ID, jsonobj):
    tempdir = os.getenv('LOGGINGDIR')
    if tempdir is None:
        return

    json.dump(
        jsonobj,
        open(os.path.join(tempdir, ID+".json"), 'w')
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

    # get time
    dt = datetime.now()
    dtstr = dt.replace(tzinfo=timezone.utc).isoformat()

    # prepare return object
    return_obj = {
        "query": data,
        "result": {
            "url": url,
            "phishing": True if results[0][0] == 1 else False,   # must specify bool value like this
            "phishing_probability": float(results[1][0, 1])
        },
        "time": dtstr
    }

    # logging
    write_log("log"+dtstr, return_obj)

    # result result
    return jsonify(return_obj)


if __name__ == "__main__":
    app.run(port=args.port)
