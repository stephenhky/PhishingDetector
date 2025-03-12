
import os
import json
import logging
from datetime import datetime, timezone

import onnxruntime
from huggingface_hub import hf_hub_download
from dotenv import load_dotenv
import boto3


load_dotenv()


REPO_ID = os.getenv("PHISHING_REPO_ID")
FILENAME = os.getenv("PHISHING_FILE_ID")
model_path = hf_hub_download(repo_id=REPO_ID, filename=FILENAME)


def write_log(file_id, object):
    lambda_client = boto3.client('lambda')
    lambda_client.invoke(
        FunctionName=os.getenv('LOGLAMBDAARN'),
        InvocationType='Event',
        Payload=json.dumps({
            "body": {"ID": file_id, "result": object}
        })
    )


def lambda_handler(event, context):
    # getting query
    logging.info(event)
    logging.info(context)
    query = event['body']
    if isinstance(query, str):
        query = json.loads(query)

    # inference
    sess = onnxruntime.InferenceSession(
        model_path,
        providers=["CPUExecutionProvider"],
    )
    results = sess.run(None, {"inputs": [query["url"]]})
    logging.info(results)

    # get time
    dt = datetime.now()
    dtstr = dt.replace(tzinfo=timezone.utc).isoformat()

    # prepare return object
    return_obj = {
        "query": query,
        "result": {
            "url": query["url"],
            "phishing": True if results[0][0] == 1 else False,  # must specify bool value like this
            "phishing_probability": float(results[1][0, 1])
        },
        "time": dtstr
    }

    # write log
    write_log("log"+dtstr, return_obj)

    # return
    return {
        'isBase64Encoded': False,
        'statusCode': 200,
        'body': json.dumps(return_obj)
    }