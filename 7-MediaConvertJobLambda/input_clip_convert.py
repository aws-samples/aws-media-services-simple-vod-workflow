#!/usr/bin/env python

import json
import os
import uuid
import boto3
import copy

from botocore.client import ClientError

def lambda_handler(event, context):

    assetID = str(uuid.uuid4())
    sourceS3Bucket = event['Records'][0]['s3']['bucket']['name']
    sourceS3Key = event['Records'][0]['s3']['object']['key']

    # this is the EDL file that got dropped in the bucket that triggered this Lambda
    sourceS3 = 's3://'+ sourceS3Bucket + '/' + sourceS3Key
    sourceS3Basename = "edl-title"
    destinationS3 = 's3://' + os.environ['DestinationBucket']
    destinationS3basename = os.path.splitext(os.path.basename(destinationS3))[0]
    
    mediaConvertRole = os.environ['MediaConvertRole']
    region = os.environ['AWS_DEFAULT_REGION']
    statusCode = 200
    body = {}
    
    # Use MediaConvert SDK UserMetadata to tag jobs with the assetID 
    # Events from MediaConvert will have the assetID in UserMedata
    jobMetadata = {'assetID': assetID}

    print (json.dumps(event))

    Settings = {}
    Settings["Inputs"] = []
    VideoSettings = {
        "AudioSelectors": {
        "Audio Selector 1": {
          "Offset": 0,
          "DefaultSelection": "DEFAULT",
          "ProgramSelection": 1
        }
      },
      "VideoSelector": {
        "ColorSpace": "FOLLOW",
        "Rotate": "DEGREE_0"
      },
      "FilterEnable": "AUTO",
      "PsiControl": "USE_PSI",
      "FilterStrength": 0,
      "DeblockFilter": "DISABLED",
      "DenoiseFilter": "DISABLED",
      "TimecodeSource": "ZEROBASED",
      "FileInput": "s3://rodeolabz-us-west-2/reinvent2019/llama_drama.mp4",
      "InputClippings": []
    }
    s3 = boto3.resource('s3')
    s3.meta.client.download_file(sourceS3Bucket, sourceS3Key, '/tmp/this.edl')

    # process the EDL  
    with open('/tmp/this.edl') as f:
        linelist = f.readlines()
        #first line is always title
        sourceS3Basename = linelist[0].split(":")[1].strip() # save the title

        iterlist = iter(linelist)
        done_looping = False
        while not done_looping:
            try:
                item = next(iterlist)
            except StopIteration:
                done_looping = True
            else:
                form_statement_list = item.split(' ')
                #if the first item is numeric, then this is the edit decision ID 
                #and this line will have the cut information
                if form_statement_list[0].isnumeric():
                    # this has the cut info
                    cut_info_list = item.split(' ')
                    print (cut_info_list)
                     #4th item from end = start of input clip
                    input_clip_start_time = cut_info_list[-4].strip()

                    #3rd item from end = end of input clip
                    input_clip_end_time = cut_info_list[-3].strip()

                    # the very next line we expect to have the user note on asset/clip name
                    # it's the first item from end of list after split
                    # assumption: the asset/clips being used are in the same bucket/path that the EDL was written to
                    clip_name = os.path.dirname(sourceS3) + "/" + next(iterlist).split(' ')[-1].strip()
                    VideoSettings["InputClippings"] = [{"StartTimecode": input_clip_start_time, "EndTimecode": input_clip_end_time}]
                    VideoSettings["FileInput"] = clip_name
                    Settings["Inputs"].append(copy.deepcopy(VideoSettings))
        print(Settings)

    try:
        # Job settings are in the lambda zip file in the current working directory
        with open('input_clipping_job.json') as json_data:
            jobSettings = json.load(json_data)
            #print(jobSettings)
        
        # get the account-specific mediaconvert endpoint for this region
        mc_client = boto3.client('mediaconvert', region_name=region)
        endpoints = mc_client.describe_endpoints()

        # add the account-specific endpoint to the client session 
        client = boto3.client('mediaconvert', region_name=region, endpoint_url=endpoints['Endpoints'][0]['Url'], verify=False)

        # Update the job settings with the source video from the S3 event and destination 
        # paths for converted videos
        jobSettings['Inputs']=Settings['Inputs']
        
        S3KeyHLS = 'assets/' + assetID + '/HLS/' + sourceS3Basename
        jobSettings['OutputGroups'][0]['OutputGroupSettings']['HlsGroupSettings']['Destination'] \
            = destinationS3 + '/' + S3KeyHLS
         
        S3KeyWatermark = 'assets/' + assetID + '/MP4/' + sourceS3Basename
        jobSettings['OutputGroups'][1]['OutputGroupSettings']['FileGroupSettings']['Destination'] \
            = destinationS3 + '/' + S3KeyWatermark
        
        S3KeyThumbnails = 'assets/' + assetID + '/Thumbnails/' + sourceS3Basename
        jobSettings['OutputGroups'][2]['OutputGroupSettings']['FileGroupSettings']['Destination'] \
            = destinationS3 + '/' + S3KeyThumbnails     

        print('jobSettings:')
        print(json.dumps(jobSettings))

        # Convert the video using AWS Elemental MediaConvert
        job = client.create_job(Role=mediaConvertRole, UserMetadata=jobMetadata, Settings=jobSettings)
        print (json.dumps(job, default=str))

    except Exception as e:
        print ('Exception: %s' % e)
        statusCode = 500
        raise

    finally:
        return {
            'statusCode': statusCode,
            'body': json.dumps(body),
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}
        }
