# Automatically collect MediaConvert CloudWatch events and store them in DynamoDB

In this module you'll use Cloudwatch and Lambda to automatically catch and store MediaConvert events.   

![Serverless event architecture](../images/simple-events.png)

You'll implement a Lambda function that will be invoked each time a MediaConvert event is detected by CloudWatch event rules.  The lambda stores the events in DynamoDB so we can examine them later.

## Prerequisites

1. You need the ability to create MediaConvert jobs for triggering the automation.  Jobs can be created from the console or you could use the watchfolder workflow from this folder: [Workflow-WatchFolderAndNotification](../Workflow-WatchfolderAndNotification/README.md).  

## Implementation Instructions

Each of the following sections provide an implementation overview and detailed, step-by-step instructions. The overview should provide enough context for you to complete the implementation if you're already familiar with the AWS Management Console or you want to explore the services yourself without following a walkthrough.

### (optional) Skip ahead with CloudFormation 
A CloudFormation template is provided for this module, if you would prefer to build the workflow automatically.  See the instructions in [README-cloudformation.md](./README-cloudformation.md).


### 1. Create a dynamodb table for storing events

Use the console to create a DyanmoDB table called `EventTable` that will be used to store all MediaConvert cloudwatch events.

1. Select the Region you've chosen to use for this workshop from the dropdown.

1. In the AWS Management Console choose **Services** then select **DynamoDB** under Storage.

1. Click on the **Create Table** button

1. Provide a name for your table such as  `EventTable` in the **Table name** box.
2. Type `id` in the **Primary key** box
3. Check the **Add sort key** radio button
4. Fill in the sort key box with `timestamp` and change the type to **Number** in the dropdown
5. Leave everything else as Default and click **Create**
7. On the **Overview** tab, select the **Manage TTL** link
8. Type in `timestampTTL` in the box and click **Continue**

![Event table](../images/dynamotable.png)


### 2. Create an IAM Role for Your Lambda function

#### Background

Every Lambda function has an IAM role associated with it. This role defines what other AWS services the function is allowed to interact with. For the purposes of this workshop, you'll need to create an IAM role that grants your Lambda function permission to interact with the  DynamoDB table created in the last step.  

#### High-Level Instructions

Use the IAM console to create a role. Name it `EventLambdaRole` and select AWS Lambda for the role type. 

Attach the managed policy called `AWSLambdaBasicExecutionRole` to this role to grant the necessary CloudWatch Logs permissions. 

Use inline policies to grant permissions to other resources needed for the lambda to execute.

#### Step-by-step instructions

1. From the AWS Management Console, click on **Services** and then select **IAM** in the Security, Identity & Compliance section.

1. Select **Roles** in the left navigation bar and then choose **Create role**.

1. Select **AWS Service** and **Lambda** for the role type, then click on the **Next:Permissions** button.

    **Note:** Selecting a role type automatically creates a trust policy for your role that allows AWS services to assume this role on your behalf. If you were creating this role using the CLI, AWS CloudFormation or another mechanism, you would specify a trust policy directly.

1. Begin typing `AWSLambdaBasicExecutionRole` in the **Filter** text box and check the box next to that role.

1. Choose **Next:Review**.

1. Repeat the search with `AmazonDynamoDBFullAccess` in the **Filter** text box and check the name next to that role.

1. Enter `EventLambdaRole` for the **Role name**.

1. Choose **Create role**.

![eventlambdarole](../images/eventlambdarole.png)




### 3. Create a Lambda Function for saving MediaConvert events

#### Background

AWS Lambda will run your code in response to events. In this step you'll build the core function that will catch and save MediaConvert events. 

#### High-Level Instructions

Use the AWS Lambda console to create a new Lambda function called `EMCEventCollector` that will process events. Use the provided [simple_event_collector.py](simple_event_collector.py) example implementation for your function code. 

Make sure to configure your function to use the `EventLambdaRole` IAM role you created in the previous section.

#### Step-by-step instructions 

1. Choose **Services** then select **Lambda** in the Compute section.

1. Choose **Create a Lambda function**.

1. Choose the **Author from scratch** button.

1. On the **Author from Scratch** panel, enter `EMCEventCollector` in the **Name** field.
2. Select **Python 3.6** for the **Runtime**.

1. Choose **Use and existing role** from the Role dropdown.

1. Select `EventLambdaRole` from the **Existing Role** dropdown.

1. Click on **Create function**.

    ![Create Lambda function screenshot](../images/lambda-simple-event-collector.png)

2. Create a zip file containing the lambda code.  In a terminal, navigate to the directory where you cloned this git repository and zip the code for the lambda.

  ```
  cd ElementalTechMarketingVODTools/1B-MediaConvert-events
  zip -r lambda.zip simple_event_collector.py
  ```

1. On the Configuration tab of the EMCEventCollector page, in the  **function code** panel:  

    1. Select **Upload a zip file** for the **Code entry type**
    2. Click **Upload** and select the zip file you created in the previous step from the dialog box. 

    1. Enter `simple_event_collector.lambda_handler` for the **Handler** field.

        ![Lambda function code screenshot](../images/lambda-simple-event-code.png)

1. On the **Environment Variables** panel of the VODLambdaConvert page, enter the following keys and values:

    1. EventTable = EventTable
    1. EventTableTTL = 1 

    ![Lambda function code screenshot](../images/lambda-simple-event-env.png)

1. On the  **Basic Settings** panel, enter the following: 
    
    1. Timeout = 2 min

1. Scroll back to the top of the page and click on the **Save** button.

### Test the lambda

1. From the main edit screen for your function, on the dropdown that says **_Select test event..._** and click on **Configure test event**.

    ![Configure test event](../images/configure-test-event.png)

1. Copy and paste the following test event into the editor:

    ```JSON
    {
      "version": "0",
      "id": "68e9a977-aa88-1fdf-405d-9aa9506393a0",
      "detail-type": "MediaConvert Job State Change",
      "source": "aws.mediaconvert",
      "account": "1234567890",
      "time": "2018-04-02T12:55:33Z",
      "region": "us-west-2",
      "resources": [
        "JOB ARN"
      ],

      "detail": {
        "timestamp": 1522673733689,
        "accountId": "ACCOUNT",
        "queue": "QUEUE ARN",
        "jobId": "1522673670949-v90e0c",
        "status": "STATUS_UPDATE",
        "userMetadata": {
          "workflow": "funnycatvideos"
        },

        "framesDecoded": 6519
      }
    }
    ```
1. Enter `EventTest` in the `Event name` box.
1. Choose **Save and test**.

1. Verify that the execution succeeded and that the **result returned by your function execution** box has:
    ```
    true
    ```

### 2. Create Cloudwatch event rule for determining what events will invoke our lambda function

#### Background

Unlike S3, MediaConvert doesn't provide a direct Event Source Mapping type for Lambdas, so we need to create a CloudWatch event rule to invoke Lambda in response to MediaConvert events.

#### High-Level Instructions

Use the AWS CloudWatch console to create a new Event Rule called `AllMediaConvertEventRule` that will trigger a Lambda when any event from source `aws:mediaconvert` occurs.  

#### Step-by-step instructions 

1. Choose **Services** then select **CloudWatch** from the AWS console.

1. Click on **Rules** in the Events section of the sidebar menu.
2. Click on **Create rule**
3. Leave the **Event source** radio button activated
4. Select `MediaConvert`from the **Service name** drop down.
5. Leave the **Event type** drop down set to `All events`
6. Click on **+Add target**
7. In the target dropdown, select the Lambda function you created in the last step.
8. Click on the **Configure details** button at the bottom of the page.
9. Enter `AllMediaConvertEventRule` for the **Name**
10. Click on the **Create rule** button

### 2. Create a role to grant Cloudwatch Event rules permission to invoke the lambda function

#### Background

Cloudwatch will need to invoke our lambda when it sees an event that matches the event rule.    

#### High-Level Instructions

Use the IAM console to create a role. Name it `EventInvokeLambda` and select **Cloudwatch Events** as the service that will use the role.  

Use inline policies to grant permissions to other resources needed for the lambda to execute.

#### Step-by-step instructions

1. From the AWS Management Console, click on **Services** and then select **IAM** in the Security, Identity & Compliance section.

1. Select **Roles** in the left navigation bar and then choose **Create role**.

1. Select **AWS Service** and **CloudWatch Events** for the service that will use the role, and **CloudWatch Events** for the use case, then click on the **Next:Permissions** button.

    **Note:** Selecting a role type automatically creates a trust policy for your role that allows AWS services to assume this role on your behalf. If you were creating this role using the CLI, AWS CloudFormation or another mechanism, you would specify a trust policy directly.

1. The required policies will already be selected.

1. Choose **Next:Review**.

1. Enter `EventInvokeLambda` for the **Role name**.

1. Choose **Create role**.

### 2. Finally test the workflow  

#### High-Level Instructions

Create a MediaConvert job and view the events from the DynamoDb console.

#### Step-by-step instructions

1. Create a MediaConvert job using the MediaConvert console or the watchfolder workflow.
2. In one browser tab, monitor the MediaConvert console to see the progress of the job.
3. In another tab, open the DyanamoDB console and open the page for your EventTable.
4. You should see new Items in the table as the MediaConvert job progresses.





