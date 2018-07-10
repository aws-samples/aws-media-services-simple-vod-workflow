#### High-Level Instructions

You may want to create restricted users to work with MediaConvert.  This section goes through creating the policy needed to complete this lab for a user that doesn't have Administrator access.  This step needs to be completed by a user with Administrator access to grant permissions.

Create an IAM Policy and name it `vod-MediaConvertUserPolicy`.  Use inline policies to grant permissions to other resources needed for the execute MediaConvert.  Attach the new policy to an IAM user.

#### Detailed Instructions - create a managed policy
1. From the AWS Management Console, click on **Services** and then select **IAM** in the Security, Identity & Compliance section.
1. Select **Policies** from the side bar menu.
1. Click on the **Create policy** button.
1. Select **Create Your Own Policy**.
1. Enter `vod-MediaConvertUserPolicy` as the policy name
1. Copy and paste the following JSON into the **Policy Document**, then select **Create** to create the policy
```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AccessMediaConvert",
            "Effect": "Allow",
            "Action": [
                "mediaconvert:*"
            ],
            "Resource": [
                "arn:aws:mediaconvert:*"
            ]
        },
        {
            "Sid": "PassRolestoMediaConvert",
            "Action": [
                "iam:ListRoles",
                "iam:PassRole"
            ],
            "Effect": "Allow",
            "Resource": "arn:aws:iam::*"
        },
        {
            "Sid": "ListWriteS3Buckets",
            "Action": "s3:*",
            "Effect": "Allow",
            "Resource": "*"
        }
    ]
}
```

#### Detailed Instructions - attach the managed policy to an IAM user

1. Select **Users** from the IAM side bar menu.
1. Click on the User Name you want to add permissions to navigate to the user Summary page.
1. Select **Add permissions** 
1. On the Grant Permissions page, select **Attach existing policies directly**
1. Enter `vod-MediaConvertUserPolicy` in the search box and then select the checkbox for the policy from the returned results. 
1. Select the **Next: Review** button on the bottom of the page.
1. Select the **Add permission** button

6. Click on Validate Policy to check for typos, then click Apply Policy