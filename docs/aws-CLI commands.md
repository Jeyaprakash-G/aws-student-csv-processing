# AWS CLI Commands — End-to-End Data Ingestion Pipeline

## 1. Project Overview

**Project Name:** Automating a Real-Time, Event-Driven Data Ingestion Pipeline for Business Transactions

**Objective:** Automate the process of monitoring a local folder, uploading files to Amazon S3, processing uploaded data using AWS Lambda, storing the data in Amazon RDS MySQL, and sending notifications through Amazon SNS.

The infrastructure is managed using AWS CLI commands wherever supported.

### AWS Services Used

* AWS CLI
* Amazon S3
* AWS Lambda
* AWS IAM
* Amazon RDS MySQL
* AWS Secrets Manager
* Amazon SNS
* Amazon SQS (optional event-processing architecture)
* Amazon CloudWatch
* AWS Lambda Layers
* Amazon VPC
* AWS Security Groups
* AWS Systems Manager Parameter Store (optional)

---

## 2. End-to-End Architecture

### Actual Implementation: Direct S3-to-Lambda Integration

```text
LOCAL WINDOWS COMPUTER
        |
        v
Python Installation
        |
        v
Install boto3 and watchdog
        |
        v
Create Local Monitoring Folder
C:\data\to_upload
        |
        v
Watchdog Python Script
        |
        v
Windows Task Scheduler
        |
        v
AWS CLI Credentials and IAM Permissions
        |
        v
AMAZON S3 BUCKET
        |
        v
S3 Object-Created Event Notification
        |
        v
AWS LAMBDA
        |
        +----------------------+
        |                      |
        v                      v
AWS SECRETS MANAGER       Amazon SNS
        |                 Notifications
        v
Amazon RDS MySQL
```

### Alternative Architecture: S3-to-SQS-to-Lambda

```text
Local Computer
      |
      v
Python Watchdog Script
      |
      v
Amazon S3
      |
      v
S3 Event Notification
      |
      v
Amazon SQS Queue
      |
      v
Lambda Event Source Mapping
      |
      v
AWS Lambda
      |
      +------> Secrets Manager
      |
      +------> Amazon RDS MySQL
      |
      +------> Amazon SNS
```

**Important:** Our hands-on implementation used direct S3-to-Lambda integration. The SQS architecture is an alternative that requires additional configuration. SQS is not automatically inserted between S3 and Lambda.

---

# PHASE 1 — LOCAL SYSTEM TO AMAZON S3

## 3. Install and Verify Python

Check whether Python is installed.

```powershell
python --version
```

Check the Python package installer.

```powershell
python -m pip --version
```

If Python is not installed, install a compatible Python version before proceeding.

## 4. Install Python Dependencies

Install Boto3 and Watchdog.

```powershell
python -m pip install boto3 watchdog
```

Verify the installed packages.

```powershell
python -m pip show boto3 watchdog
```

### Purpose

* `boto3`: Allows Python to communicate with AWS services.
* `watchdog`: Monitors filesystem events, such as file creation and modification.

## 5. Create the Local Monitoring Folder

Create the folder that Watchdog will monitor.

```powershell
New-Item -ItemType Directory -Path "C:\data\to_upload" -Force
```

### Folder Purpose

```text
C:\
└── data\
    └── to_upload\
        ├── student.csv
        ├── student2.csv
        └── other-files.csv
```

When a file is created or modified in this folder, the Python script detects the event and attempts to upload the file to S3.

The local folder path must match the `LOCAL_FOLDER` variable in `upload_to_s3.py`.

## 6. Configure AWS CLI

Check the AWS CLI version.

```powershell
aws --version
```

Configure AWS credentials if they are not already configured.

```powershell
aws configure
```

Enter the appropriate values when prompted:

* AWS Access Key ID
* AWS Secret Access Key
* Default region: `ap-south-1`
* Default output format: `json`

For production environments, prefer IAM roles or other temporary credential mechanisms where applicable. Do not store credentials in your GitHub repository.

## 7. Verify AWS Access

```powershell
aws sts get-caller-identity
```

This command displays the identity associated with the active AWS credentials.

If the command succeeds, the CLI can authenticate to AWS.

---

# PHASE 2 — AMAZON S3 CONFIGURATION

## 8. List Existing S3 Buckets

```powershell
aws s3 ls
```

Our project used the bucket:

`student-csv-ingestion-jp`

Verify that it exists.

```powershell
aws s3 ls s3://student-csv-ingestion-jp/
```

## 9. Create an S3 Bucket (If Required)

Only run this if the bucket does not already exist.

```powershell
aws s3 mb s3://YOUR-UNIQUE-BUCKET-NAME --region ap-south-1
```

S3 bucket names must be globally unique.

Replace the placeholder with the actual bucket name.

## 10. Upload a File Manually for Testing

```powershell
aws s3 cp "C:\data\to_upload\student.csv" s3://student-csv-ingestion-jp/uploads/
```

Verify the upload.

```powershell
aws s3 ls s3://student-csv-ingestion-jp/uploads/
```

### Automated Upload

The actual automation is performed by:

`scripts/upload_to_s3.py`

The script:

1. Monitors the configured local folder.
2. Detects file creation or modification.
3. Waits briefly for the file-writing operation to finish.
4. Uploads the file using Boto3.
5. Places the uploaded object under the configured S3 prefix.

The script requires valid AWS credentials and permission to upload objects to the bucket.

---

# PHASE 3 — WINDOWS TASK SCHEDULER

## 11. Automate the Watchdog Script

The Watchdog script must run continuously to monitor the local folder.

Windows Task Scheduler can start the script automatically when you sign in or when the computer starts.

### Create a Scheduled Task Using PowerShell

Example:

```powershell
schtasks /Create /TN "S3WatchdogUpload" /SC ONLOGON /TR "python C:\path\to\upload_to_s3.py" /F
```

Replace `C:\path\to\upload_to_s3.py` with the actual path of the script.

### Start the Scheduled Task

```powershell
schtasks /Run /TN "S3WatchdogUpload"
```

### Query the Task Status

```powershell
schtasks /Query /TN "S3WatchdogUpload" /V /FO LIST
```

### Stop the Task

```powershell
schtasks /End /TN "S3WatchdogUpload"
```

### Delete the Task

```powershell
schtasks /Delete /TN "S3WatchdogUpload" /F
```

### Important Configuration Notes

* Use the full path to `python.exe` if Task Scheduler cannot locate Python.
* Use the full path to the Python script.
* Configure the task to start in the directory containing the script, if necessary.
* Configure the appropriate user account and permissions.
* The local computer must be running, and the monitoring script must be active.
* A logon trigger runs when the configured user signs in; it does not automatically mean the script runs every five minutes.
* If you configure a recurring trigger, use Task Scheduler's repetition settings or an appropriate scheduled-task configuration.

**Important:** Task Scheduler starts the Python process. Watchdog itself detects filesystem events; Task Scheduler does not monitor the folder.

---

# PHASE 4 — IAM CONFIGURATION

## 12. Create an IAM Execution Role for Lambda

Lambda requires an execution role to access other AWS services.

The role has two distinct components:

1. A trust policy allowing the Lambda service to assume the role.
2. Permission policies allowing the function to access the required resources.

### Step 1: Create the Trust Policy

Create a file named:

`lambda-trust-policy.json`

Content:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
```

### Step 2: Create the IAM Role

```powershell
aws iam create-role --role-name ProcessingLambdaRole --assume-role-policy-document file://lambda-trust-policy.json
```

### Step 3: Attach the Basic Lambda Execution Policy

```powershell
aws iam attach-role-policy --role-name ProcessingLambdaRole --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
```

This managed policy provides basic permissions for sending Lambda logs to CloudWatch Logs.

### Step 4: Add Required Service Permissions

The Lambda execution role may need permissions for:

* Reading objects from the specified S3 bucket, if the function reads the CSV file.
* Reading database credentials from Secrets Manager.
* Connecting to RDS through the configured network.
* Publishing messages to SNS.
* Accessing other services explicitly used by the application.
* Reading messages from SQS, if SQS is configured as the Lambda event source.

Create a least-privilege policy JSON containing the required actions and resource ARNs.

For example, save the appropriate permissions in:

`lambda-permissions-policy.json`

Then create the policy:

```powershell
aws iam create-policy --policy-name ProcessingLambdaPermissions --policy-document file://lambda-permissions-policy.json
```

Attach it to the role, replacing `ACCOUNT_ID` with your AWS account ID:

```powershell
aws iam attach-role-policy --role-name ProcessingLambdaRole --policy-arn arn:aws:iam::ACCOUNT_ID:policy/ProcessingLambdaPermissions
```

**Important:** The policy document must contain the actual resource ARNs and permissions required by the application. Do not use broad administrator permissions simply to make the integration work.

### Step 5: Verify the Role

```powershell
aws iam get-role --role-name ProcessingLambdaRole
```

List the attached managed policies:

```powershell
aws iam list-attached-role-policies --role-name ProcessingLambdaRole
```

### Note About VPC Permissions

If the Lambda function is configured inside a VPC, it needs appropriate permissions for the Lambda service to manage the required network interfaces.

The `AWSLambdaBasicExecutionRole` policy does not provide these VPC networking permissions. Configure the necessary permissions, commonly through `AWSLambdaVPCAccessExecutionRole`, when applicable.

The Lambda function and RDS security groups, subnet configuration, and routes must also permit the required database connectivity.

---

# PHASE 5 — AMAZON RDS MYSQL

## 13. Verify the RDS Database

List database instances.

```powershell
aws rds describe-db-instances --region ap-south-1
```

Retrieve details for the project database.

```powershell
aws rds describe-db-instances --db-instance-identifier devops-rds-mysql --region ap-south-1
```

The response includes information such as:

* Database engine
* Database status
* Endpoint address
* Database port
* VPC security groups
* Subnet group

### Important RDS Configuration

The database must have:

* An appropriate DB subnet group.
* A security group allowing the required MySQL connection from the Lambda security group.
* A database endpoint accessible from the Lambda network.
* Valid database credentials.
* The necessary VPC connectivity.

For MySQL, the default port is `3306`.

### Create an RDS Database

If creating a new database through CLI, first configure the required VPC subnets, security groups, DB subnet group, credentials, and other database settings.

Example command structure:

```powershell
aws rds create-db-instance --db-instance-identifier YOUR-DB-IDENTIFIER --db-instance-class YOUR-DB-INSTANCE-CLASS --engine mysql --master-username YOUR-DB-USERNAME --manage-master-user-password --allocated-storage 20 --db-subnet-group-name YOUR-DB-SUBNET-GROUP --vpc-security-group-ids YOUR-SECURITY-GROUP-ID --region ap-south-1
```

This is a template, not a reproduction of the exact RDS creation command used in our earlier session. Adjust the engine version, storage, instance class, subnet group, security groups, and other parameters to match the intended deployment.

Using `--manage-master-user-password` allows RDS to manage the master password through Secrets Manager for supported configurations.

Do not place an actual database password in GitHub or in a shared command history.

---

# PHASE 6 — AWS SECRETS MANAGER

## 14. Verify the Database Secret

List the available secrets.

```powershell
aws secretsmanager list-secrets --region ap-south-1
```

Describe a specific secret.

```powershell
aws secretsmanager describe-secret --secret-id YOUR-SECRET-NAME --region ap-south-1
```

### Lambda Integration

The Lambda function retrieves the database credentials from Secrets Manager instead of hardcoding the password in the Python source.

The Lambda execution role must have permission to retrieve the intended secret.

For a customer-managed KMS encryption key, additional KMS permissions may be required.

Do not publish secret values or database passwords in this document.

---

# PHASE 7 — CREATE THE PYMYSQL LAMBDA LAYER

## 15. Install PyMySQL Locally

Our existing layer uses:

* Layer name: `devops-pymysql-layer`
* PyMySQL version: `1.2.3`
* Runtime: Python 3.14
* Architecture: ARM64
* Region: `ap-south-1`

Create the layer directory:

```powershell
New-Item -ItemType Directory -Path "C:\lambda-rds-project\layer\python" -Force
```

Install the required library:

```powershell
py -m pip install PyMySQL==1.2.3 --target "C:\lambda-rds-project\layer\python"
```

## 16. Package the Library into a ZIP File

Create the ZIP package.

```powershell
Compress-Archive -Path "C:\lambda-rds-project\layer\python" -DestinationPath "C:\lambda-rds-project\devops-pymysql-layer.zip" -Force
```

Verify that the ZIP has a top-level `python/` directory.

Expected structure:

```text
devops-pymysql-layer.zip
└── python/
    ├── pymysql/
    └── pymysql-1.2.3.dist-info/
```

The `python/` directory must be at the root of the ZIP archive, not nested inside the full Windows directory path.

## 17. Publish the Lambda Layer Using AWS CLI

Create the layer version:

```powershell
aws lambda publish-layer-version --layer-name devops-pymysql-layer --description "PyMySQL 1.2.3 layer for RDS MySQL connectivity" --zip-file fileb://C:/lambda-rds-project/devops-pymysql-layer.zip --compatible-runtimes python3.14 --compatible-architectures arm64 --region ap-south-1
```

This command publishes a new version of the layer.

The response includes a `LayerVersionArn`.

Save that ARN for the next step.

## 18. Attach the Layer to the Lambda Function

Replace `YOUR-LAYER-VERSION-ARN` with the actual ARN returned by the previous command.

```powershell
aws lambda update-function-configuration --function-name devops-rds-lambda-connection --layers YOUR-LAYER-VERSION-ARN --region ap-south-1
```

**Important:** The `--layers` option specifies the layer list for the function. If the function already uses other layers, include their ARNs as well so you do not unintentionally remove them.

Verify the configuration:

```powershell
aws lambda get-function-configuration --function-name devops-rds-lambda-connection --region ap-south-1
```

---

# PHASE 8 — CREATE AND CONFIGURE THE LAMBDA FUNCTION

## 19. Verify Existing Lambda Functions

```powershell
aws lambda list-functions --region ap-south-1
```

Retrieve the function configuration.

```powershell
aws lambda get-function-configuration --function-name devops-rds-lambda-connection --region ap-south-1
```

## 20. Create a Lambda Function Using CLI

To create a new Lambda function, prepare a deployment ZIP containing the Python handler and any required application files.

Create the function using the execution role ARN.

```powershell
aws lambda create-function --function-name devops-rds-lambda-connection --runtime python3.14 --handler lambda_function.lambda_handler --role YOUR-LAMBDA-EXECUTION-ROLE-ARN --zip-file fileb://lambda-deployment.zip --architectures arm64 --timeout 30 --memory-size 256 --region ap-south-1
```

This is a template. Use the actual handler, role ARN, ZIP path, timeout, memory, runtime, and architecture for your deployment.

If your application code is already deployed, do not recreate the function unnecessarily.

## 21. Update Lambda Code

When the function code changes, create an updated deployment ZIP and upload it.

```powershell
aws lambda update-function-code --function-name devops-rds-lambda-connection --zip-file fileb://lambda-deployment.zip --region ap-south-1
```

## 22. Configure Environment Variables

If the application requires non-secret configuration values, they can be supplied as environment variables.

Example:

```powershell
aws lambda update-function-configuration --function-name devops-rds-lambda-connection --environment "Variables={DB_HOST=YOUR-RDS-ENDPOINT,DB_NAME=YOUR-DATABASE,SECRET_NAME=YOUR-SECRET-NAME}" --region ap-south-1
```

This example replaces the function's environment-variable configuration. Include any existing required variables when updating it.

Store passwords in Secrets Manager rather than as plain-text environment variables.

---

# PHASE 9 — AMAZON S3 EVENT NOTIFICATION

## 23. Configure S3 to Invoke Lambda Directly

Our actual hands-on workflow used direct S3-to-Lambda integration.

First, allow S3 to invoke the Lambda function.

Obtain the AWS account ID:

```powershell
aws sts get-caller-identity
```

Add a resource-based permission to the Lambda function.

Replace the placeholders with the correct account ID and bucket name.

```powershell
aws lambda add-permission --function-name devops-rds-lambda-connection --statement-id AllowS3Invoke --action lambda:InvokeFunction --principal s3.amazonaws.com --source-arn arn:aws:s3:::YOUR-S3-BUCKET --source-account YOUR-AWS-ACCOUNT-ID --region ap-south-1
```

## 24. Configure the S3 Bucket Notification

Create a file named:

`s3-notification.json`

Example:

```json
{
  "LambdaFunctionConfigurations": [
    {
      "Id": "S3ToLambda",
      "LambdaFunctionArn": "YOUR-LAMBDA-FUNCTION-ARN",
      "Events": [
        "s3:ObjectCreated:*"
      ],
      "Filter": {
        "Key": {
          "FilterRules": [
            {
              "Name": "prefix",
              "Value": "uploads/"
            }
          ]
        }
      }
    }
  ]
}
```

Replace `YOUR-LAMBDA-FUNCTION-ARN` with the actual Lambda function ARN.

Apply the configuration:

```powershell
aws s3api put-bucket-notification-configuration --bucket YOUR-S3-BUCKET --notification-configuration file://s3-notification.json --region ap-south-1
```

Verify the notification configuration:

```powershell
aws s3api get-bucket-notification-configuration --bucket YOUR-S3-BUCKET --region ap-south-1
```

**Important:** `put-bucket-notification-configuration` replaces the bucket's existing notification configuration. Include all existing required notifications in the JSON before applying it.

S3 notification destinations must be configured with the appropriate permissions. Avoid notification loops—for example, having a Lambda write a new object back to the same triggering prefix without appropriate filtering.

---

# PHASE 10 — OPTIONAL S3 → SQS → LAMBDA

## 25. Create an SQS Queue

This section applies only if you want to implement the alternative SQS-based architecture.

Create a queue:

```powershell
aws sqs create-queue --queue-name business-transaction-queue --region ap-south-1
```

Retrieve the queue URL and ARN:

```powershell
aws sqs get-queue-attributes --queue-url YOUR-QUEUE-URL --attribute-names QueueArn --region ap-south-1
```

## 26. Configure S3 to Send Events to SQS

The SQS queue must have a resource policy allowing the intended S3 bucket to send messages.

Create a queue policy that grants `sqs:SendMessage` to the S3 service principal, restricted to the appropriate bucket ARN and source account.

Apply the policy using:

```powershell
aws sqs set-queue-attributes --queue-url YOUR-QUEUE-URL --attributes file://sqs-attributes.json --region ap-south-1
```

The `sqs-attributes.json` file must contain the queue's `Policy` attribute.

Next, configure the S3 bucket's notification configuration to include the SQS queue ARN.

S3-to-SQS notifications must satisfy the applicable regional and permission requirements.

## 27. Configure SQS as a Lambda Event Source

The Lambda execution role needs the required SQS polling permissions, including receiving and deleting messages and retrieving queue attributes.

Create the event source mapping:

```powershell
aws lambda create-event-source-mapping --function-name devops-rds-lambda-connection --event-source-arn YOUR-SQS-QUEUE-ARN --batch-size 1 --enabled --region ap-south-1
```

Verify the mapping:

```powershell
aws lambda list-event-source-mappings --function-name devops-rds-lambda-connection --region ap-south-1
```

**Important:** When using SQS as the Lambda event source, the Lambda event payload has an SQS `Records` structure. The application must read the S3 notification contained in each SQS message body rather than treating the outer event as a direct S3 event.

The SQS path is optional and was not part of our original direct S3-to-Lambda implementation.

---

# PHASE 11 — SNS NOTIFICATIONS

## 28. Verify SNS Topics

List existing topics.

```powershell
aws sns list-topics --region ap-south-1
```

Create a topic if one does not already exist:

```powershell
aws sns create-topic --name business-transaction-notifications --region ap-south-1
```

Save the returned topic ARN.

## 29. Grant Lambda Permission to Publish to SNS

The Lambda execution role needs permission to publish to the intended topic.

Add the appropriate `sns:Publish` action and topic ARN to the role's permissions policy.

## 30. Configure a Lambda Destination

Lambda supports asynchronous invocation destinations.

To configure an SNS destination for failed asynchronous invocations:

```powershell
aws lambda put-function-event-invoke-config --function-name devops-rds-lambda-connection --maximum-retry-attempts 2 --destination-config '{"OnFailure":{"Destination":"YOUR-SNS-TOPIC-ARN"}}' --region ap-south-1
```

For successful asynchronous invocations, use the `OnSuccess` destination field instead.

**Important:** Lambda asynchronous invocation destinations are not identical to synchronous invocation responses or S3 event notifications. The destination configuration applies to asynchronous invocations. Choose the destination behavior according to the intended workflow.

Verify the configuration:

```powershell
aws lambda get-function-event-invoke-config --function-name devops-rds-lambda-connection --region ap-south-1
```

---

# PHASE 12 — CLOUDWATCH LOGS AND TROUBLESHOOTING

## 31. Verify Lambda Logs

Retrieve recent logs:

```powershell
aws logs tail "/aws/lambda/devops-rds-lambda-connection" --since 1h --region ap-south-1
```

The execution role needs appropriate CloudWatch Logs permissions.

## 32. Check S3 Objects

```powershell
aws s3 ls s3://student-csv-ingestion-jp/uploads/
```

## 33. Check Lambda Configuration

```powershell
aws lambda get-function-configuration --function-name devops-rds-lambda-connection --region ap-south-1
```

## 34. Check RDS Status

```powershell
aws rds describe-db-instances --db-instance-identifier devops-rds-mysql --region ap-south-1
```

## 35. Common Issues

### Python Script Cannot Upload to S3

Check:

* AWS credentials.
* IAM permissions.
* Bucket name and region.
* Local file path.
* Python script logs.

### Lambda Cannot Import PyMySQL

Check:

* Layer attachment.
* Layer ZIP structure.
* Compatible Python runtime.
* Compatible architecture.

### Lambda Cannot Connect to RDS

Check:

* RDS endpoint.
* MySQL port.
* VPC and subnet configuration.
* Lambda and RDS security groups.
* Secrets Manager permissions.
* Database credentials.

### S3 Does Not Trigger Lambda

Check:

* S3 notification configuration.
* Lambda resource-based permissions.
* Correct bucket ARN.
* Object key filters.
* CloudWatch logs.

### SQS Does Not Trigger Lambda

Check:

* Event source mapping.
* Queue ARN.
* SQS polling permissions.
* Queue visibility timeout.
* Lambda logs and message-processing errors.

---

# PHASE 13 — PROJECT VALIDATION

## 36. End-to-End Test

1. Verify that AWS CLI authentication works.
2. Confirm that the S3 bucket exists.
3. Confirm that the local Watchdog script is running.
4. Create a test CSV file in the monitored local folder.
5. Verify that the file appears in S3.
6. Confirm that the configured S3 notification invokes Lambda directly or sends a message to SQS.
7. Check Lambda execution logs in CloudWatch.
8. Verify that Lambda retrieves the database credentials from Secrets Manager.
9. Verify that the application processes the data and writes the intended records to RDS MySQL.
10. Verify the configured SNS notification behavior.

The expected result is a functioning automated data ingestion pipeline with monitoring and notification capabilities.

---

# Security Best Practices

* Never commit AWS access keys, secret access keys, or database passwords.
* Use least-privilege IAM policies.
* Keep database credentials in Secrets Manager.
* Restrict RDS access to the required security groups.
* Avoid publicly exposing the database.
* Review S3 bucket permissions and notification configuration.
* Use placeholders for account-specific ARNs and resource identifiers in public documentation.
* Verify resource names and configuration before executing commands.

---

# Conclusion

This project documents the end-to-end automation of file ingestion from a local Windows computer to Amazon S3, followed by event-driven processing through AWS Lambda, optional SQS-based buffering, Amazon RDS MySQL integration, Secrets Manager credential retrieval, and SNS notifications.

The local automation uses Python, Boto3, Watchdog, and Windows Task Scheduler. AWS resources can be inspected and configured using AWS CLI, while the Lambda execution role and resource policies control service-to-service access.
