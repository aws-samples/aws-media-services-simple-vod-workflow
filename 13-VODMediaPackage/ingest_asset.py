import json
import boto3
import time
import os

def lambda_handler(event, context):
    empvod =  boto3.client('mediapackage-vod')

    packaging_group_id = os.environ['PACKAGING_GROUP_ID']
    hls_playlist_paths = []
    for output_detail in event['detail']['outputGroupDetails']:
        if output_detail['type'] == 'HLS_GROUP':
            hls_playlist_paths = output_detail['playlistFilePaths']
    if len(hls_playlist_paths) > 0:
        for hls_path in hls_playlist_paths:
            try:
                #check to see if packaging group exists
                response = empvod.describe_packaging_group(
                    Id=packaging_group_id
                )
            except empvod.exceptions.NotFoundException as e:
                print(e)
                # if packaging group not found, create one plus 3 configurations
                response = empvod.create_packaging_group(
                    Id=packaging_group_id
                )
                # create the packaging configurations, taking mostly defaults
                # CMAF
                response = empvod.create_packaging_configuration(
                    CmafPackage = {
                            'HlsManifests': [
                                {
                                },
                            ],
                            'SegmentDurationSeconds': 2
                        },
                    Id = packaging_group_id + "_CMAF_config",
                    PackagingGroupId = packaging_group_id
                )
                # Smooth
                response = empvod.create_packaging_configuration(  
                    MssPackage={
                        'MssManifests': [
                        {
                        },
                        ],
                        'SegmentDurationSeconds': 2
                    },
                    Id = packaging_group_id + "_MSS_config",
                    PackagingGroupId = packaging_group_id
                )
                # DASH
                response = empvod.create_packaging_configuration(  
                    DashPackage={ 
                        'DashManifests': [
                        {
                        },
                        ],
                        'SegmentDurationSeconds': 2
                    },
                    Id = packaging_group_id + "_DASH_config",
                    PackagingGroupId = packaging_group_id
                )
            
            # create asset after packaging group has been verified or created
            source_arn = "arn:aws:s3:::" + hls_path.split('s3://')[1]
            #asset_id is manifest file name + current time
            asset_id = hls_path.split('/')[-1].split('.')[0] + str(int(time.time()))
            response = empvod.create_asset(
                Id=asset_id,
                PackagingGroupId=packaging_group_id,
                SourceArn=source_arn,
                SourceRoleArn=os.environ['SOURCE_ROLE_ARN']
            )

    return {
        'statusCode': 200,
        'body': json.dumps(response)
    }

