### (Optional) Instructions for running CloudFormation

1. Make sure your region is set to US-West-Oregon for this lab.
2. From the AWS Management Console, click on **Services** and then select **CloudFormation**.
3. Select **Create stack** to go to the **Create stack** page
4. Select the **Upload a template to Amazon S3** checkbox then select **Choose file**
5. Navigate to the directory where you downloaded the lab.  Then select **1-IAMandS3->MediaConvertIAMandS3.yaml**. Then select **Open**.
6. Select **Next** to move to the **Specify details** page.
7. Enter `vod` for the in the **Stack name** box.  Note: you can choose other stack names, but using "vod" will create resource with names consistent with the rest of the lab.
8. Select **Next** to move to the **Options** page.  Leave this page as defaults.
9. Select **Next** to move to the **Review** page.
10. Select the checkbox to acknowledge creating resources, then select **Create**
11. Wait for the stack to be created.
12. From the Stacks page, find the Stack called **vod**.
13. Go to the Stack details page and expand the Outputs section of the page.  You will find two outputs there:
    
    * **MediaConvertRole** is the ARN for the AWS Role that can be passed to MediaConvert to grant access to S3 and other account resources MediaConvert needs to process jobs.
14. Save this page in a browser tab or save the ARNs to be used in future steps of the Workshop.

Move forward to the next module  [**AWS Elemental Media Convert Jobs**](../2-MediaConvertJobs/README.md).