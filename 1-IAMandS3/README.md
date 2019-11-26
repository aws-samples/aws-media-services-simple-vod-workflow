# AWS IAM and S3 User Module

This module guides the participant in setting up the AWS resources needed to complete the Video on Demand workshop. You will create and configure an AWS S3 bucket to store outputs from MediaConvert. You will also create a role that allows MediaConvert access to the resources in your account that are needed to convert videos. 

You can optionally create a restricted user with access only to the resources needed to complete the lab.

## Prerequisites

### Region

MediaConvert is available in several regions. But for the purpose of this lab, we will use the **US West (Oregon)** region.

In order to complete this workshop you'll need an AWS Account with access to create policies and roles within the AWS Identity and Access Management (IAM) service. 

The signed-in user must have the AdministratorAccess policy or a policy that allows the user to access all actions for the mediaconvert service and at least read access to CloudWatch. The steps for creating a policy for AWS Elemental MediaPConvert is covered near the end of this module.

The code and instructions in this workshop assume only one student is using a given AWS account at a time. If you try sharing an account with another student, you'll run into naming conflicts for certain resources. You can work around this by either using a suffix in your resource names or using distinct Regions, but the instructions do not provide details on the changes required to make this work.

### (Optional) Skip ahead with CloudFormation

If you would like to skip this part of the lab and move on the the next module, a CloudFormation script is provided in this folder in `MediaConvertIAMandS3.yaml`.  

[**Instructions to create resources in this section using CloudFormation**](README-cf.md)

Otherwise, continue to the next section.

## 1. Create an IAM Role to Use with AWS Elemental MediaConvert

MediaConvert will will need to be granted permissions to read and write files from your S3 buckets and generate CloudWatch events as it processes videos.  MediaConvert is granted the permissions it needs by assuming a role that is passed to it when you create a job.

#### High-Level Instructions

Use the IAM console to create a new role. Name it `vod-MediaConvertRole` and select AWS MediaConvert.

#### Detailed Instructions

1. From the AWS Management Console, click on **Services** and then select **IAM** in the Security, Identity & Compliance section.

1. Select **Roles** in the left navigation bar and then choose **Create role**.

1. Select **AWS Service** and **MediaConvert** for the role type, then click on the **Next:Permissions** button.

    **Note:** Selecting a role type automatically creates a trust policy for your role that allows AWS services to assume this role on your behalf. If you were creating this role using the CLI, AWS CloudFormation or another mechanism, you would specify a trust policy directly.

1. Click on **Next:Tags**. 

1. Click on **Next:Review**.

1. Enter `vod-MediaConvertRole` for the **Role name**.

1. Choose **Create role**.

1. Copy and save off the Role ARN of the role you just created using your favorite editor. You will be needing this in the subsequent modules.

## 2. Create an S3 bucket to store and host MediaConvert outputs

In this section, you will use the AWS console to create an S3 bucket to store video and image outputs from MediaConvert and host a simple web page that can be used to play out the videos.  Later, the resulting videos and images will be played out using the S3 https resource using several different players both inside and outside of the the amazonaws domain.  

In order to facilitate https access from anonymous sources inside and outside the amazonaws domain, such as video players on the internet, you will add the following settings to the S3 bucket:

* a bucket policy that enables public read   
* a policy for Cross Origin Resource Sharing (CORS) 

#### Detailed instructions 

1. In the AWS Management Console choose **Services** then select **S3** under Storage.

1. Choose **+Create Bucket**.

1. Provide a globally unique name for your bucket such as `vod-lastname`.

1. Select the Region you've chosen to use for this workshop from the dropdown.

1. Choose **Create** in the lower left of the dialog without selecting a bucket to copy settings from.

1. From the S3 console select the bucket you just created and go to the Overview page.
1. Select the **Properties** tab and click on the **Static website hosting** tile.  
1. Select the **Use this bucket to host a website** box.
1. Enter `index.html` in the **Index document** box.
1. Select **Save**.
1. Select the **Permissions** tab.
1. Under **Block public access**, click on the **Edit** button.
1. Uncheck **Block all public access** and click the **Save** button.
1. Type `confirm` in the textbox that pops up and click **Confirm**.
1. Select **Bucket policy** and paste the following JSON into the bucket policy editor.
1. Replace the text **YOUR-BUCKETNAME** with the name of the bucket you created earlier in this module.

    ```
    {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AddPerm",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::YOUR-BUCKETNAME/*"
        }
    ]
    }
    ```
1. Click on **Save**
1. Next, click on **CORS configuration** and enter the following XML into the **CORS configuration editor**.
    ```
    <?xml version="1.0" encoding="UTF-8"?>
    <CORSConfiguration xmlns="http://s3.amazonaws.com/doc/2006-03-01/">
    <CORSRule>
        <AllowedOrigin>*</AllowedOrigin>
        <AllowedMethod>GET</AllowedMethod>
        <MaxAgeSeconds>3000</MaxAgeSeconds>
        <AllowedHeader>*</AllowedHeader>
    </CORSRule>
    </CORSConfiguration>
    ```

1. Select **Save**

## (Optional) Adding AWS Elemental MediaConvert permissions to an IAM user

You may want to create restricted users to work with MediaConvert.  This section goes through creating the policy needed to complete this lab for a user that doesn't have Administrator access.  This step needs to be completed by a user with Administrator access to grant permissions.

[**Instructions to create a restricted user**](README-user.md)

## Completion

At the end of the module you have created a IAM Role to allow access from MediaConvert to resources in your account. You have also (optionally ) added MediaConvert permissions to a user.

Move forward to the next module  [**AWS Elemental Media Convert Jobs**](../2-MediaConvertJobs/README.md).