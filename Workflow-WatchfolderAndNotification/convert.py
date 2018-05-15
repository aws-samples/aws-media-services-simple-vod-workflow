#!/usr/bin/env python

import glob
import json
import os
import uuid
import boto3
import datetime
import random
from urlparse import urlparse
import logging

from botocore.client import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

S3 = boto3.resource('s3')

def handler(event, context):
    '''
    Watchfolder handler - this lambda is triggered when video objects are uploaded to the 
    SourceS3Bucket/inputs folder.

    It will look for two sets of file inputs:
        SourceS3Bucket/inputs/SourceS3Key:
            the input video to be converted
        
        SourceS3Bucket/jobs/*.json:
            job settings for MediaConvert jobs to be run against the input video. If 
            there are no settings files in the jobs folder, then the Default job will be run 
            from the job.json file in lambda environment. 
    
    Ouput paths stored in outputGroup['OutputGroupSettings']['DashIsoGroupSettings']['Destination']
    are constructed from the name of the job settings files as follows:
        
        s3://<MediaBucket>/<basename(job settings filename)>/<basename(input)>/<Destination value from job settings file>

    '''

    assetID = str(uuid.uuid4())
    sourceS3Bucket = event['Records'][0]['s3']['bucket']['name']
    sourceS3Key = event['Records'][0]['s3']['object']['key']
    sourceS3 = 's3://'+ sourceS3Bucket + '/' + sourceS3Key
    destinationS3 = 's3://' + os.environ['DestinationBucket']
    mediaConvertRole = os.environ['MediaConvertRole']
    application = os.environ['Application']
    region = os.environ['AWS_DEFAULT_REGION']
    statusCode = 200
    jobs = []
    job = {}
    
    # Use MediaConvert SDK UserMetadata to tag jobs with the assetID 
    # Events from MediaConvert will have the assetID in UserMedata
    jobMetadata = {}
    jobMetadata['assetID'] = assetID
    jobMetadata['application'] = application
    jobMetadata['input'] = sourceS3
    
    try:    
        
        # Build a list of jobs to run against the input.  Use the settings files in WatchFolder/jobs
        # if any exist.  Otherwise, use the default job.
        
        jobInput = {}
        # Iterates through all the objects in jobs folder of the WatchFolder bucket, doing the pagination for you. Each obj
        # contains a jobSettings JSON
        bucket = S3.Bucket(sourceS3Bucket)
        for obj in bucket.objects.filter(Prefix='jobs/'):
            if obj.key != "jobs/":
                jobInput['filename'] = obj.key
                logger.info('jobInput: %s', jobInput['filename'])

                jobInput['settings'] = json.loads(obj.get()['Body'].read())
                logger.info(json.dumps(jobInput['settings'])) 
                
                jobs.append(jobInput)
        
        # Use Default job settings in the lambda zip file in the current working directory
        if not jobs:
            
            with open('job.json') as json_data:
                jobInput['filename'] = 'Default'
                logger.info('jobInput: %s', jobInput['filename'])

                jobInput['settings'] = json.load(json_data)
                logger.info(json.dumps(jobInput['settings']))

                jobs.append(jobInput)
                 
        # get the account-specific mediaconvert endpoint for this region
        mediaconvert_client = boto3.client('mediaconvert', region_name=region)
        endpoints = mediaconvert_client.describe_endpoints()

        # add the account-specific endpoint to the client session 
        client = boto3.client('mediaconvert', region_name=region, endpoint_url=endpoints['Endpoints'][0]['Url'], verify=False)
        
        for j in jobs:
            jobSettings = j['settings']
            jobFilename = j['filename']

            # Save the name of the settings file in the job userMetadata
            jobMetadata['settings'] = jobFilename

            # Update the job settings with the source video from the S3 event 
            jobSettings['Inputs'][0]['FileInput'] = sourceS3

            # Update the job settings with the destination paths for converted videos.  We want to replace the
            # destination bucket of the output paths in the job settings, but keep the rest of the
            # path
            destinationS3 = 's3://' + os.environ['DestinationBucket'] + '/' \
                + os.path.splitext(os.path.basename(sourceS3Key))[0] + '/' \
                + os.path.splitext(os.path.basename(jobFilename))[0]                 

            for outputGroup in jobSettings['OutputGroups']:
                
                logger.info("outputGroup['OutputGroupSettings']['Type'] == %s", outputGroup['OutputGroupSettings']['Type']) 
                
                if outputGroup['OutputGroupSettings']['Type'] == 'FILE_GROUP_SETTINGS':
                    templateDestination = outputGroup['OutputGroupSettings']['FileGroupSettings']['Destination']
                    templateDestinationKey = urlparse(templateDestination).path
                    logger.info("templateDestinationKey == %s", templateDestinationKey)
                    outputGroup['OutputGroupSettings']['FileGroupSettings']['Destination'] = destinationS3+templateDestinationKey

                elif outputGroup['OutputGroupSettings']['Type'] == 'HLS_GROUP_SETTINGS':
                    templateDestination = outputGroup['OutputGroupSettings']['HlsGroupSettings']['Destination']
                    templateDestinationKey = urlparse(templateDestination).path
                    logger.info("templateDestinationKey == %s", templateDestinationKey)
                    outputGroup['OutputGroupSettings']['HlsGroupSettings']['Destination'] = destinationS3+templateDestinationKey
                
                elif outputGroup['OutputGroupSettings']['Type'] == 'DASH_ISO_GROUP_SETTINGS':
                    templateDestination = outputGroup['OutputGroupSettings']['DashIsoGroupSettings']['Destination']
                    templateDestinationKey = urlparse(templateDestination).path
                    logger.info("templateDestinationKey == %s", templateDestinationKey)
                    outputGroup['OutputGroupSettings']['DashIsoGroupSettings']['Destination'] = destinationS3+templateDestinationKey

                elif outputGroup['OutputGroupSettings']['Type'] == 'DASH_ISO_GROUP_SETTINGS':
                    templateDestination = outputGroup['OutputGroupSettings']['DashIsoGroupSettings']['Destination']
                    templateDestinationKey = urlparse(templateDestination).path
                    logger.info("templateDestinationKey == %s", templateDestinationKey)
                    outputGroup['OutputGroupSettings']['DashIsoGroupSettings']['Destination'] = destinationS3+templateDestinationKey
                
                elif outputGroup['OutputGroupSettings']['Type'] == 'MS_SMOOTH_GROUP_SETTINGS':
                    templateDestination = outputGroup['OutputGroupSettings']['MsSmoothGroupSettings']['Destination']
                    templateDestinationKey = urlparse(templateDestination).path
                    logger.info("templateDestinationKey == %s", templateDestinationKey)
                    outputGroup['OutputGroupSettings']['MsSmoothGroupSettings']['Destination'] = destinationS3+templateDestinationKey
                else:
                    logger.error("Exception: Unknown Output Group Type %s", outputGroup['OutputGroupSettings']['Type'])
                    statusCode = 500
            
            logger.info(json.dumps(jobSettings))

            # Convert the video using AWS Elemental MediaConvert
            job = client.create_job(Role=mediaConvertRole, UserMetadata=jobMetadata, Settings=jobSettings)

    except Exception as e:
        logger.error('Exception: %s', e)
        statusCode = 500
        raise

    finally:
        return {
            'statusCode': statusCode,
            'body': json.dumps(job, indent=4, sort_keys=True, default=str),
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}
        }
