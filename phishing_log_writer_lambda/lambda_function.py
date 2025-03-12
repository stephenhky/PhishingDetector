
import os
import json
import logging

import boto3


def lambda_handler(event, context):
    # getting query
    logging.info(event)
    logging.info(context)
    query = event['body']
    if isinstance(query, str):
        query = json.loads(query)

    # get parameters
    file_id = query.get('ID')
    detection_result = query.get('result')

    # write
    jsonfilepath = os.path.join('/', 'tmp', file_id+".json")
    json.dump(detection_result, open(jsonfilepath, 'w'))

    # copy to S3
    s3_bucket = os.getenv('S3BUCKET')
    s3_client = boto3.client('s3')
    s3_client.upload_file(jsonfilepath, s3_bucket, file_id+".json")

    return {
        'isBase64Encoded': False,
        'statusCode': 200,
        'body': json.dumps(event)
    }