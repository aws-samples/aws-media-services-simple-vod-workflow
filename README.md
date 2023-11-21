# This project has been archived.  

# AWS Video On Demand with MediaConvert Workshop

This workshop takes you through development of a video on demand (VOD)workflow using an encoder in the cloud to convert video content stored in Amazon S3 into new formats for storage, reuse and delivery. We will explore encoding video in different codecs and package formats, quality levels and output sizes for file based and streaming delivery.  We will also look at how you can modify videos using clipping and stitching, add captions, detect Ads in input videos and burn in information to video to help with providing additional information about the video on playout.  

The workshop is broken up into multiple modules. Prerequisites for each module are listed at the start of the module README file.  Some  of the modules have AWS CloudFormation templates available that you can use to launch the necessary resources without manually creating them yourself if you'd like to skip ahead.

# Workshop Requirements

### AWS Account

In order to complete this workshop you'll need an AWS Account with access to create AWS MediaConvert, IAM, S3, and Lambda resources. The code and instructions in this workshop assume only one student is using a given AWS account at a time. If you try sharing an account with another student, you'll run into naming conflicts for certain resources. You can work around these by appending a unique suffix to the resources that fail to create due to conflicts, but the instructions do not provide details on the changes required to make this work.

### Billing

MediaConvert jobs will incur charges based on the region you are using for the workshop at the rates described in the MediaConvert pricing page: https://aws.amazon.com/mediaconvert/pricing/ .

**Each MediaConvert job from this lab produces outputs with the following characteristics:**

ABR stack 
* 3 outputs: 1280x720, 960x540, 680x360

MP4
* 1 output: 1280x720

Thumbnails
* 1 output: 1280x720

All ouputs:
* MPEG-2 Codec
* 30 - 60 FPS
* 1.5 - 2 minutes long depending on which job in the lab you are running.

**Other lab resources**

S3 and other resources you will launch as part of this workshop are eligible for the AWS free tier if your account is less than 12 months old. See the [AWS Free Tier page](https://aws.amazon.com/free/) for more details.

### Browser

We recommend you use the latest version of Chrome to complete this workshop.

### Video player

Videos can be played out in the browser if the browser supports them.  We will also use:
* **JW Player Stream Tester** https://developer.jwplayer.com/tools/stream-tester/ 

### Text Editor

You will need a local text editor for making minor updates to configuration files.

### Download the Workshop

You will need to download this project to your computer in order to create the browser page, run CloudFormation templates, and to work with caption files.

# Workshop Modules

- [**AWS IAM and S3**](1-IAMandS3/README.md) - This module guides the participant in configuring permissions for the AWS services used in this workshop. You will learn how to create a policy that permits users access to AWS Elemental MediaConvert in your account.  You will also create a role to pass to MediaConvert so it can access resources in your account it needs to run jobs.

- [**AWS Elemental MediaConvert Jobs**](2-MediaConvertJobs/README.md) - This module guides the participant in creating an AWS Elemental MediaConvert job to convert an HLS input into HLS, MP4 and Thumbnail outputs. You will learn about file based and adaptive bitrate delivery and the basics of producing video output for different purposes.

- [**Modifying AWS Elemental MediaConvert Inputs**](3-Inputs/README.md) - This module guides the participant in clipping and stitching inputs to AWS MediaConvert. You will explore other types on Input modications are available.

- [**Modifying AWS Elemental MediaConvert Outputs**](4-Outputs/README.md) - This module guides the participant in different kinds of information that they can "burn-in" to a video ouput. They will create a video with timecodes and watermarks burned in to the elemental video stream of one of the outputs of their job.

- [**Working with Captions**](5-Captions/README.md) - This module guides the participant in creating media assets with burned in caption generated from a side-car captions file.  


- [**Automating Jobs with Lambda and S3 Event Triggers**](7-MediaConvertJobLambda/README.md) - This module guides the participant in creating an automated "watchfolder" workflow.  Video files added to an S3 bucket automatically trigger a MediaConvert job to run on the uploaded files.

- [**VOD Ad Insertion with AWS Elemental MediaTailor**](11-VODMediaTailor) - This module guides the participant in inserting ads to their HLS media asset using the AWS Elemental MediaTailor service.

# Start the Workshop

Move forward to the first module for [**AWS IAM and S3**](1-IAMandS3/README.md).

# Credits

_Sea Waves Sound_ in TRAILER.mp4 recorded by Mike Koenig.  Licensed under the Creative Commons Attribution 3.0 license.  

Captions text in CAPTIONS_en.srt and CAPTIONS_ru.srt © copyright Blender Foundation | www.sintel.org.  Licenced under the Creative Commons Attribution 3.0 license.

# Contributors

Alex Burkleaux

Eddie Goynes

Jeremy Johnson
