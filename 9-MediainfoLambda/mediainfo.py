#!/usr/bin/env python3.6
import boto3
import datetime
import json
import time
import decimal
from botocore.client import ClientError
from boto3 import resource
from boto3.dynamodb.conditions import Key
import logging
import subprocess
#import urllib
from urllib.parse import urlparse
import timecode
from timecode import Timecode
import xmltodict
import logging
import os
import traceback

# Helper class to convert a DynamoDB item to JSON.
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)

DYNAMO_CLIENT = boto3.resource('dynamodb')

SIGNED_URL_EXPIRATION = 300

logger = logging.getLogger('boto3')
logger.setLevel(logging.INFO)

def get_signed_url(expires_in, bucket, obj):
    """
    Generate a signed URL
    :param expires_in:  URL Expiration time in seconds
    :param bucket:
    :param obj:         S3 Key name
    :return:            Signed URL
    """
    s3_cli = boto3.client("s3")
    presigned_url = s3_cli.generate_presigned_url('get_object', Params={'Bucket': bucket, 'Key': obj},
                                                  ExpiresIn=expires_in)
    return presigned_url

def lambda_handler(event, context): 
    
    print(json.dumps(event))

    tsevent = int(datetime.datetime.strptime(event["time"], "%Y-%m-%dT%H:%M:%SZ").timestamp())
    
    try:
        # Get environment variables set on the CloudFormation stack
        MEDIAINFOTABLE = os.environ['MediainfoTable']
        MEDIAINFOTABLETTL = os.environ['MediainfoTableTTL']
        
        MEDIAINFO_RETENTION_PERIOD = (3600 * 24 * int(MEDIAINFOTABLETTL))

        # Loop through input videos in the event
        for input in event['detail']['inputDetails']:
            s3_path = input['uri']
            urlp = urlparse(s3_path)
            # Extract the Key and Bucket names for the inputs
            key = urlp[2]
            key = key.lstrip('/')
            bucket = urlp[1]
            
            signed_url = get_signed_url(SIGNED_URL_EXPIRATION, bucket, key)
            logger .info("Signed URL: {}".format(signed_url))
            
            print ("bucket and key "+bucket+" "+key)
            
            # Launch MediaInfo
            # Pass the signed URL of the uploaded asset to MediaInfo as an input
            # MediaInfo will extract the technical metadata from the asset
            # The extracted metadata will be outputted in XML format and
            # stored in the variable xml_output
            xml_output = subprocess.check_output(["./mediainfo", "--full", "--output=XML", signed_url])
            print(xml_output)
            
            json_output = xmltodict.parse(xml_output)
            
            input['mediainfo'] = json_output['Mediainfo']
            
            #print(json.dumps(json_output, indent=4, cls=DecimalEncoder))

        # add expirtation timestamp for dynamo and save the event in dynamo
        job_input_info = event['detail']
        job_input_info["timestamp"] = tsevent
        job_input_info["timestampTTL"] = tsevent + MEDIAINFO_RETENTION_PERIOD
        
        s = json.dumps(job_input_info, cls=DecimalEncoder)
        job_input_info = json.loads(s, parse_float=decimal.Decimal)
        table = DYNAMO_CLIENT.Table(MEDIAINFOTABLE)
        response = table.put_item(Item = job_input_info)
        print(json.dumps(response, cls=DecimalEncoder))
        
    except Exception as e:
        print('An error occured {}'.format(e))
        traceback.print_stack()
        raise
    else:
        return True
