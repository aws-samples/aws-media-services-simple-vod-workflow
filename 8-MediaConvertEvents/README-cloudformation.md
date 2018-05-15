### Launching the Stack on AWS

A CloudFormation template is provided for this module in the file `simple-events.yaml.yaml` to build the workflow automatically. Click **Launch Stack** to launch the template in your account in the region of your choice : 

Region| Launch
------|-----
US East (N. Virginia) | [![Launch in us-east-1](http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/images/cloudformation-launch-stack-button.png)](https://console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/new?stackName=emc-events&templateURL=https://s3.amazonaws.com/rodeolabz-us-east-1/vodtk/1b-mediaconvert-events/simple-events.yaml)
US West (Oregon) | [![Launch in us-west-2](http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/images/cloudformation-launch-stack-button.png)](https://console.aws.amazon.com/cloudformation/home?region=us-west-2#/stacks/new?stackName=emc-events&templateURL=https://s3.amazonaws.com/rodeolabz-us-west-2/vodtk/1b-mediaconvert-events/simple-events.yaml)


The information about the resources created is in the **Outputs** tab of the stack.  Save this in a browser tab so you can use it later when you create other stacks and MediaConvert jobs.

![outputs](../images/cf-simple-events.png)

