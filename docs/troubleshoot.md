# AWS DevOps Project — Troubleshooting Guide

## Project Name

**Automating a Real-Time, Event-Driven Data Ingestion Pipeline for Business Transactions**

## 1. Project Overview

This document captures the major troubleshooting scenarios encountered while implementing the end-to-end AWS data ingestion pipeline.

The project automates file uploads from a local Windows machine to Amazon S3, processes uploaded files using AWS Lambda, stores the processed data in Amazon RDS MySQL, and sends notifications through Amazon SNS.

### Technologies Used

* Windows 10
* Python
* Boto3
* Watchdog
* Windows Task Scheduler
* AWS CLI
* Amazon S3
* AWS Lambda
* AWS IAM
* Amazon VPC
* VPC Endpoints
* Amazon RDS MySQL
* AWS Secrets Manager
* AWS Lambda Layers
* Amazon SNS
* Amazon SQS (optional architecture)
* Amazon CloudWatch

### End-to-End Workflow

```text
Local Windows Machine
        |
        v
Python + Watchdog
        |
        v
Windows Task Scheduler
        |
        v
Amazon S3
        |
        v
S3 Object-Created Event
        |
        v
AWS Lambda
        |
        +-------------------------+
        |                         |
        v                         v
Secrets Manager              Amazon SNS
        |
        v
Amazon RDS MySQL
        |
        v
Application Database
        |
        v
Student/Transaction Table
```

**Alternative architecture:**

```text
Amazon S3
    |
    v
Amazon SQS
    |
    v
AWS Lambda
    |
    v
Amazon RDS MySQL
    |
    v
Amazon SNS
```

The original hands-on implementation used direct S3-to-Lambda integration. The SQS-based workflow is an alternative that requires additional configuration.

---

# 2. Troubleshooting: Local System and Python

## Issue 1: Python Environment and Dependency Installation

### Problem

The local automation script required Python and the necessary libraries to communicate with AWS and monitor the local folder.

### Root Cause

The Python environment needed the required packages before the automation script could execute successfully.

### Solution

Verified the Python installation:

```powershell
python --version
```

Verified the package installer:

```powershell
python -m pip --version
```

Installed the required packages:

```powershell
python -m pip install boto3 watchdog
```

Verified the installed packages:

```powershell
python -m pip show boto3 watchdog
```

### Result

The local Python environment was prepared to execute the folder-monitoring and S3-upload automation.

---

## Issue 2: Watchdog Local Folder Monitoring

### Problem

Files created in the local folder needed to be uploaded automatically to Amazon S3 without manually executing an upload command for every file.

### Root Cause

The local folder needed to be monitored by a continuously running Watchdog process.

### Solution

Configured the Python script to monitor:

```text
C:\data\to_upload
```

The script used:

* `Observer` to monitor the directory.
* `FileSystemEventHandler` to handle filesystem events.
* `on_created()` to detect newly created files.
* `on_modified()` to detect file modifications.
* Boto3 to upload the files to S3.

The script monitored the directory recursively.

### Result

Files such as `student2.txt` and `student3.txt` were uploaded to the configured S3 bucket.

### Verification

```powershell
aws s3 ls s3://jeyaprakash-devops-automation-2026/uploads/
```

**Note:** The bucket above was used in the earlier local-upload exercise. The later event-driven pipeline also used `student-csv-ingestion-jp`. Verify which bucket is configured in the current script.

---

## Issue 3: Duplicate Upload Events

### Problem

The Watchdog script could attempt to upload the same file more than once.

### Root Cause

A file creation operation can generate both creation and modification events.

If both `on_created()` and `on_modified()` trigger uploads, the same file can be processed multiple times.

### Solution

The script should prevent duplicate processing by using an appropriate strategy, such as:

* Handling only the necessary event types.
* Tracking files currently being processed.
* Waiting until the file has finished writing.
* Checking file stability before uploading.
* Implementing idempotent processing where appropriate.

### Result

The risk of duplicate uploads and unnecessary processing can be reduced.

**Important:** Uploading the same filename to the same S3 key normally overwrites the existing object when versioning is not involved. Duplicate event handling should still be addressed because downstream Lambda processing may run more than once.

---

## Issue 4: Windows Task Scheduler Automation

### Problem

The Python Watchdog script needed to start automatically instead of requiring manual execution after every sign-in.

### Root Cause

Watchdog only monitors the folder while its Python process is running.

Creating a scheduled task does not automatically mean that the Python process is continuously active.

### Solution

Configured Windows Task Scheduler to start the Python script.

Previously recorded configuration:

```text
Task Name:
S3 Student Folder Watcher

Python Executable:
C:\Users\hp\AppData\Local\Programs\Python\Python313\python.exe

Python Script:
C:\data\upload_to_s3_watch.py

Start In:
C:\data
```

Example command to inspect the task:

```powershell
schtasks /Query /TN "S3 Student Folder Watcher" /V /FO LIST
```

To start the task manually:

```powershell
schtasks /Run /TN "S3 Student Folder Watcher"
```

### Result

The task could be started and its status checked through Windows Task Scheduler.

### Additional Verification

Check the following if automatic execution fails:

1. Correct Python executable path.
2. Correct Python script path.
3. Correct working directory.
4. Correct Windows user account and permissions.
5. Task Scheduler trigger configuration.
6. AWS credentials available to the scheduled process.
7. Whether the Python process remains running.

A logon trigger starts the task when the configured user signs in. A five-minute repetition schedule must be configured separately if required.

---

# 3. Troubleshooting: AWS CLI and Credentials

## Issue 5: AWS CLI Authentication and Access

### Problem

The local Python script needed valid AWS credentials to communicate with Amazon S3.

### Root Cause

Boto3 requires valid credentials and appropriate IAM permissions to access AWS resources.

### Solution

Verified the AWS CLI installation:

```powershell
aws --version
```

Checked the active AWS identity:

```powershell
aws sts get-caller-identity
```

Listed S3 buckets:

```powershell
aws s3 ls
```

### Result

The successful identity check confirmed that the configured AWS credentials could authenticate to AWS.

### Additional Verification

If authentication fails, check:

* AWS CLI credential configuration.
* IAM user or role permissions.
* Expired temporary credentials.
* AWS region configuration.
* Whether Task Scheduler runs under a different Windows user account.

Never commit AWS access keys or secret access keys to GitHub.

---

# 4. Troubleshooting: Amazon S3

## Issue 6: Local Files Were Not Appearing in S3

### Problem

Files created in the monitored local folder were expected to appear in the S3 bucket automatically.

### Root Cause

The upload workflow depends on several components working together:

1. Python process running.
2. Watchdog monitoring the correct folder.
3. Valid AWS credentials.
4. S3 upload permissions.
5. Correct bucket name.
6. Correct S3 key prefix.

### Solution

Verified the bucket:

```powershell
aws s3 ls
```

Checked the target prefix:

```powershell
aws s3 ls s3://jeyaprakash-devops-automation-2026/uploads/
```

Uploaded a test file manually:

```powershell
aws s3 cp "C:\data\to_upload\student.csv" s3://YOUR-BUCKET-NAME/uploads/
```

### Result

Manual upload testing helps distinguish a Python/Watchdog issue from an AWS permission or bucket configuration issue.

If manual upload succeeds but automatic upload fails, investigate the Python script and its runtime environment.

---

## Issue 7: S3 VPC Endpoint Was Missing

### Problem

The VPC did not have the required S3 VPC endpoint configuration for the intended private-network access path.

### Root Cause

A workload running in a private subnet may need an appropriate network path to reach Amazon S3.

An S3 Gateway VPC Endpoint provides private connectivity to S3 through supported VPC route tables without requiring an Internet Gateway or NAT Gateway for that S3 traffic.

### Solution

Created an S3 Gateway VPC Endpoint and associated it with the relevant route tables.

Example command:

```bash
aws ec2 create-vpc-endpoint \
  --vpc-id YOUR-VPC-ID \
  --service-name com.amazonaws.ap-south-1.s3 \
  --vpc-endpoint-type Gateway \
  --route-table-ids YOUR-ROUTE-TABLE-ID \
  --region ap-south-1
```

Replace the placeholders with the actual VPC and route table identifiers.

### Verification

```bash
aws ec2 describe-vpc-endpoints --region ap-south-1
```

### Result

The VPC has an S3 endpoint configuration for the associated route tables.

**Important:** An S3 VPC endpoint is relevant when a workload accesses S3 through that VPC. A local Windows computer uploading directly to S3 through the public AWS endpoint does not require this VPC endpoint.

The endpoint does not automatically grant S3 permissions. IAM policies, bucket policies, and any endpoint policy must still permit the intended operations.

---

# 5. Troubleshooting: VPC DNS Configuration

## Issue 8: VPC DNS Hostnames and DNS Resolution

### Problem

The VPC's DNS configuration needed to support service endpoint name resolution.

### Root Cause

The VPC DNS settings were not configured as required for the intended architecture.

### Solution

Enabled DNS support:

```bash
aws ec2 modify-vpc-attribute \
  --vpc-id YOUR-VPC-ID \
  --enable-dns-support \
  --region ap-south-1
```

Enabled DNS hostnames:

```bash
aws ec2 modify-vpc-attribute \
  --vpc-id YOUR-VPC-ID \
  --enable-dns-hostnames \
  --region ap-south-1
```

### Verification

```bash
aws ec2 describe-vpc-attribute \
  --vpc-id YOUR-VPC-ID \
  --attribute enableDnsSupport \
  --region ap-south-1
```

```bash
aws ec2 describe-vpc-attribute \
  --vpc-id YOUR-VPC-ID \
  --attribute enableDnsHostnames \
  --region ap-south-1
```

### Result

The VPC DNS attributes can be checked independently to confirm their current state.

**Technical note:** DNS support and DNS hostnames are separate settings. Enabling them does not by itself resolve every Lambda-to-RDS connectivity problem. Routes, security groups, subnet configuration, and service endpoint accessibility must also be correct.

---

# 6. Troubleshooting: Lambda Execution Role and IAM Policies

## Issue 9: Lambda Could Not Access All Required AWS Resources

### Problem

The Lambda function needed to interact with multiple AWS services, but the required permissions were not all available through the initially configured role and policies.

### Root Cause

The Lambda execution role must explicitly have permission to perform each required operation.

The default Lambda execution role does not automatically provide access to S3, Secrets Manager, RDS database operations, SNS, or SQS.

### Solution

Reviewed the Lambda execution role and added the required IAM permissions.

The role consists of two important components.

**1. Trust policy**

Allows the Lambda service to assume the execution role.

Example:

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

**2. Permission policies**

The role must have permissions for the operations performed by the function.

| AWS Service           | Example IAM Permission                                              | Purpose                                                |
| --------------------- | ------------------------------------------------------------------- | ------------------------------------------------------ |
| CloudWatch Logs       | `logs:CreateLogGroup`, `logs:CreateLogStream`, `logs:PutLogEvents`  | Write execution logs                                   |
| Amazon S3             | `s3:GetObject`                                                      | Read uploaded files                                    |
| Secrets Manager       | `secretsmanager:GetSecretValue`                                     | Retrieve database credentials                          |
| Amazon SNS            | `sns:Publish`                                                       | Publish notifications                                  |
| Amazon SQS            | `sqs:ReceiveMessage`, `sqs:DeleteMessage`, `sqs:GetQueueAttributes` | Process SQS messages when configured                   |
| AWS KMS               | Appropriate decrypt permissions, if required                        | Decrypt secrets encrypted with a customer-managed key  |
| Lambda VPC networking | Appropriate ENI permissions                                         | Support VPC network interface management when required |

### Basic Lambda Execution Policy

The basic execution policy can be attached using:

```bash
aws iam attach-role-policy \
  --role-name ProcessingLambdaRole \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
```

### Verify Attached Policies

```bash
aws iam list-attached-role-policies \
  --role-name ProcessingLambdaRole
```

### Verify Inline Policies

```bash
aws iam list-role-policies \
  --role-name ProcessingLambdaRole
```

### Result

The role can be reviewed to identify missing service permissions and correct them.

**Important:** IAM permission to retrieve database credentials is different from permission to connect to MySQL. Secrets Manager access does not automatically grant database access.

Similarly, RDS connectivity is controlled by network configuration and database-level authentication and privileges, not by an IAM policy alone.

For VPC-connected Lambda functions, check whether the required VPC networking permissions have been granted. The basic execution policy does not provide these permissions.

---

# 7. Troubleshooting: Lambda Layer and PyMySQL

## Issue 10: Lambda Required PyMySQL to Connect to RDS MySQL

### Problem

The Lambda function required a MySQL client library to connect to the RDS database.

### Root Cause

The PyMySQL library needed to be available in the Lambda execution environment.

### Solution

Created a custom Lambda Layer containing PyMySQL.

Previously recorded layer configuration:

```text
Layer Name:
devops-pymysql-layer

PyMySQL Version:
1.2.3

Runtime:
Python 3.14

Architecture:
ARM64

Region:
ap-south-1
```

Installed the library into the required directory:

```powershell
py -m pip install PyMySQL==1.2.3 --target .\python
```

Packaged the `python` directory into a ZIP file.

Expected ZIP structure:

```text
devops-pymysql-layer.zip
└── python/
    ├── pymysql/
    └── pymysql-1.2.3.dist-info/
```

Published the layer and attached its version ARN to the Lambda function.

### Verification

```bash
aws lambda get-function-configuration \
  --function-name devops-rds-lambda-connection \
  --region ap-south-1
```

### Result

The function configuration can be checked to confirm that the expected layer ARN is attached.

### Additional Checks

If Python cannot import PyMySQL, verify:

* The ZIP contains the top-level `python/` directory.
* The layer is attached to the correct Lambda function.
* The layer runtime is compatible.
* The layer architecture is compatible.
* The deployed function uses the intended runtime and architecture.

---

# 8. Troubleshooting: Lambda Timeout While Retrieving Secrets

## Issue 11: Lambda Timed Out During Secrets Manager Access

### Problem

During earlier testing, the Lambda function timed out while retrieving the database password from Secrets Manager.

The initial timeout was three seconds, and a later test used a longer timeout.

### Root Cause

The function needed to communicate with Secrets Manager. When a Lambda function runs inside a VPC, its network configuration can prevent access to public AWS service endpoints unless an appropriate network path exists.

Potential causes include:

* Missing NAT Gateway or appropriate VPC endpoint.
* Incorrect subnet routing.
* Security group restrictions.
* DNS configuration issues.
* Insufficient execution timeout.

### Solution

Reviewed the Lambda network configuration and service connectivity.

The previous troubleshooting history records that the Secrets Manager access issue was resolved after network-related configuration changes.

The precise final network change should be confirmed against the deployed VPC configuration before documenting a specific endpoint or route as the definitive fix.

### Verification

Check the function configuration:

```bash
aws lambda get-function-configuration \
  --function-name devops-rds-lambda-connection \
  --region ap-south-1
```

Check recent logs:

```bash
aws logs tail \
  "/aws/lambda/devops-rds-lambda-connection" \
  --since 1h \
  --region ap-south-1
```

### Result

The Lambda function was subsequently able to retrieve the database password and proceed with the RDS connection.

---

# 9. Troubleshooting: RDS MySQL Database Name and Error 1044

## Issue 12: MySQL Error 1044 — Access Denied to the Database

### Problem

During the RDS MySQL integration, the application encountered MySQL error `1044`.

The Lambda function could not access the intended application database.

### Root Cause

The application database name and the database configured in the Lambda connection settings did not match the intended application configuration.

The initial configuration used the MySQL system database name, while the application was expected to use its own database, such as `student_db`.

MySQL error 1044 generally indicates that the database user does not have sufficient privileges to access the specified database. A database-name mismatch can lead to access attempts against the wrong database, but the error alone does not prove that this was the only cause.

### Solution

Reviewed the following connection settings:

* RDS endpoint.
* Database username.
* Database name.
* Database privileges.
* Lambda configuration.
* Secrets Manager credentials.

Updated the application configuration to use the intended application database rather than assuming the default `mysql` system database was the target.

The intended database name was:

```text
student_db
```

The exact spelling and capitalization must match the database used in the application.

### Verification

Connect to MySQL using an authorized database client and check the available databases:

```sql
SHOW DATABASES;
```

Check the current database:

```sql
SELECT DATABASE();
```

Check the tables in the application database:

```sql
SHOW TABLES;
```

### Result

After the database configuration and access issue were corrected, the Lambda function was able to proceed with the intended application database workflow.

### Important Database Concepts

* `mysql` is a MySQL system database.
* `student_db` is an example application database name.
* A database user requires the appropriate database privileges.
* A valid database endpoint does not guarantee permission to access every database.
* IAM permissions do not automatically grant MySQL table-level access.

---

# 10. Troubleshooting: Lambda Could Not Insert Records into RDS

## Issue 13: Data Was Not Inserted into the Application Table

### Problem

The Lambda function could connect to RDS, but inserting the processed data into the application table did not work as expected.

### Root Cause

Potential causes include:

* Incorrect database name.
* Incorrect table name.
* Incorrect column names.
* SQL statement errors.
* Missing database privileges.
* Incorrect CSV parsing.
* Data type mismatches.
* Missing or invalid field values.
* Transaction changes not committed.
* Incorrect database credentials.

The previous troubleshooting history confirms that database access and application-database configuration required correction. It does not establish that every item in this list occurred in the project.

### Solution

Reviewed the database connection configuration and the SQL insert logic.

Checked that:

1. Lambda connected to the correct RDS endpoint.
2. The correct application database was selected.
3. The intended table existed.
4. The insert statement referenced valid column names.
5. The database user had the necessary insert privileges.
6. Values from the CSV were mapped to the expected columns.
7. The transaction was committed where required.
8. Exceptions were logged rather than silently ignored.

### Verification

From an authorized MySQL client, verify the table:

```sql
SHOW TABLES;
```

Inspect the table definition:

```sql
DESCRIBE student_transactions;
```

Inspect the inserted records:

```sql
SELECT * FROM student_transactions LIMIT 10;
```

Replace `student_transactions` with the actual application table name.

### Result

After correcting the application database configuration and insert logic, the application could proceed with inserting data into the intended table.

**Security note:** Avoid logging database passwords, secret values, or sensitive transaction data.

---

# 11. Troubleshooting: S3 Object Retrieval and CSV Processing

## Issue 14: Lambda Needed to Retrieve and Analyse the Uploaded File

### Problem

The Lambda function needed to retrieve the uploaded object and process its contents.

### Root Cause

An S3 event contains information about the bucket and object key. It does not automatically contain the complete contents of the uploaded file.

The function must retrieve the object from S3 before processing the file data.

### Solution

Reviewed the following workflow:

1. Receive the S3 event.
2. Extract the bucket name.
3. Extract and decode the object key where required.
4. Retrieve the object using the S3 API.
5. Read the CSV content.
6. Validate the data.
7. Map the CSV fields to database columns.
8. Insert or update the application database records.
9. Send the appropriate notification.

### Verification

Check that the Lambda execution role includes the required S3 read permission.

Verify that the object exists:

```bash
aws s3 ls s3://YOUR-BUCKET-NAME/uploads/
```

Check the Lambda logs:

```bash
aws logs tail \
  "/aws/lambda/devops-rds-lambda-connection" \
  --since 1h \
  --region ap-south-1
```

### Result

The processing workflow can be verified from the S3 event through file retrieval and database insertion.

---

# 12. Troubleshooting: Lambda Execution Order and Application Logic

## Issue 15: Lambda Code Did Not Execute in the Intended Sequence

### Problem

The Lambda code contained processing steps that were not organized in the intended execution order.

For example, some numbered steps appeared out of sequence.

This made the code difficult to understand and troubleshoot.

### Root Cause

The application logic needed a clear execution sequence, with dependencies handled before the operations that rely on them.

### Solution

Organized the application workflow into a logical sequence:

**Step 1 — Receive the Event**

Identify the S3 object or SQS message that triggered the function.

**Step 2 — Validate the Event**

Check the event structure, bucket name, object key, and required fields.

**Step 3 — Retrieve the S3 Object**

Download or read the uploaded file through the appropriate S3 API.

**Step 4 — Parse and Validate the File**

Read the CSV data and validate the expected columns and values.

**Step 5 — Retrieve Database Credentials**

Retrieve the database credentials from Secrets Manager.

**Step 6 — Connect to RDS MySQL**

Establish the database connection using the correct endpoint and application database.

**Step 7 — Insert or Update Records**

Execute the intended SQL operations and commit the transaction where appropriate.

**Step 8 — Send the Notification**

Publish a success or failure notification according to the configured notification design.

**Step 9 — Close Resources and Log the Result**

Close database resources and log the processing outcome.

### Result

The code structure became easier to understand, maintain, and troubleshoot.

### Important Design Consideration

The actual order can differ depending on the implementation.

For example, credentials may be retrieved before reading the file if the application is designed that way. What matters is that every operation executes after its dependencies are available and that errors are handled correctly.

---

# 13. Troubleshooting: SNS Notification Failures

## Issue 16: Lambda Could Not Send Notifications Through SNS

### Problem

The application needed to send success or failure notifications, but the notification operation did not work as expected.

### Root Cause

Potential causes include:

* Missing `sns:Publish` permission.
* Incorrect SNS topic ARN.
* Wrong AWS region.
* Incorrect topic configuration.
* Invalid message or notification logic.
* Errors being caught without being logged.

### Solution

Verified the available SNS topics:

```bash
aws sns list-topics --region ap-south-1
```

Reviewed the Lambda execution role to confirm that it had the required `sns:Publish` permission for the intended topic.

Verified that the topic ARN configured in the application matched the actual topic.

### Verification

Inspect the Lambda execution logs:

```bash
aws logs tail \
  "/aws/lambda/devops-rds-lambda-connection" \
  --since 1h \
  --region ap-south-1
```

If authorized to test publishing manually, use:

```bash
aws sns publish \
  --topic-arn YOUR-SNS-TOPIC-ARN \
  --message "Test notification from the AWS CLI" \
  --region ap-south-1
```

### Result

The SNS integration can be tested separately from the Lambda processing logic, making it easier to isolate notification permission or configuration issues.

**Important:** An SNS topic receiving a message and a Lambda asynchronous destination are different mechanisms. Configure the one required by the architecture.

---

# 14. Troubleshooting: S3 Event Notifications

## Issue 17: S3 Event Notifications Did Not Trigger the Expected Workflow

### Problem

Uploading an object to S3 was expected to invoke the Lambda function.

### Root Cause

S3 event-driven processing depends on the notification configuration and permissions being correct.

Potential causes include:

* Missing S3 notification configuration.
* Incorrect Lambda ARN.
* Missing Lambda resource-based permission.
* Incorrect bucket ARN.
* Incorrect object-key filter.
* Uploading a file outside the configured prefix.
* The notification targeting the wrong AWS region or resource.

### Solution

Reviewed the S3 notification configuration and Lambda resource-based policy.

Verified that the S3 bucket was authorized to invoke the intended Lambda function.

Checked the bucket notification configuration and confirmed that the uploaded object matched the configured event filters.

### Verification

Inspect Lambda configuration:

```bash
aws lambda get-function-configuration \
  --function-name devops-rds-lambda-connection \
  --region ap-south-1
```

Inspect Lambda logs:

```bash
aws logs tail \
  "/aws/lambda/devops-rds-lambda-connection" \
  --since 1h \
  --region ap-south-1
```

### Result

S3 event processing can be isolated from the local upload process by testing the S3 notification and Lambda integration independently.

---

# 15. Troubleshooting: SQS and Lambda Integration

## Issue 18: SQS Event Processing Did Not Work as Expected

### Problem

In the alternative architecture, SQS was intended to buffer messages before Lambda processed them.

### Root Cause

SQS-based Lambda processing requires a correctly configured event source mapping and sufficient SQS polling permissions.

Additionally, an SQS-triggered Lambda receives an SQS event structure. The S3 notification is contained inside the message body.

### Solution

Verified the Lambda event source mapping and queue configuration.

Confirmed that the execution role had the required SQS polling permissions.

Ensured that the Lambda code could parse the SQS message body and then process the embedded S3 event.

### Verification

```bash
aws lambda list-event-source-mappings \
  --function-name devops-rds-lambda-connection \
  --region ap-south-1
```

### Result

The queue and event source mapping can be inspected independently from the database processing logic.

**Project note:** This section documents the alternative SQS design. The original hands-on implementation used direct S3-to-Lambda integration.

---

# 16. Troubleshooting: Lambda Networking and RDS Connectivity

## Issue 19: Lambda Could Not Connect to RDS

### Problem

The Lambda function needed to connect to the RDS MySQL database, but successful AWS authentication alone did not guarantee database connectivity.

### Root Cause

Database connectivity requires the correct network path, security rules, database endpoint, and credentials.

### Solution

Reviewed the following components:

* Lambda VPC configuration.
* Lambda subnet selection.
* RDS subnet group.
* Lambda security group.
* RDS security group.
* Route tables.
* DNS settings.
* RDS endpoint and port.
* Secrets Manager credentials.
* Database username and privileges.

### Verification

Inspect the Lambda VPC configuration:

```bash
aws lambda get-function-configuration \
  --function-name devops-rds-lambda-connection \
  --region ap-south-1
```

Inspect the RDS database:

```bash
aws rds describe-db-instances \
  --db-instance-identifier devops-rds-mysql \
  --region ap-south-1
```

### Result

Network connectivity and database authentication can be investigated as separate troubleshooting areas.

**Important:** A security group allowing traffic is not sufficient if the subnets, routes, DNS, or database configuration are incorrect.

---

# 17. Troubleshooting: Secrets Manager and Database Authentication

## Issue 20: Lambda Retrieved Credentials but Database Access Still Failed

### Problem

The function needed to retrieve the database password from Secrets Manager and use it to connect to MySQL.

### Root Cause

Successfully retrieving a secret does not guarantee that the credentials are valid for the intended database.

Possible causes include:

* Incorrect secret identifier.
* Incorrect username or password.
* Wrong database endpoint.
* Wrong database name.
* Insufficient MySQL privileges.
* Incorrect secret JSON field names.
* Incorrect credential parsing in the Lambda code.

### Solution

Reviewed the secret configuration and confirmed that the Lambda function extracted the intended fields.

Verified that the endpoint and database name matched the intended RDS instance and application database.

### Verification

List available secrets:

```bash
aws secretsmanager list-secrets --region ap-south-1
```

Inspect a secret's metadata:

```bash
aws secretsmanager describe-secret \
  --secret-id YOUR-SECRET-NAME \
  --region ap-south-1
```

### Result

Secrets Manager access and MySQL database authentication can be tested independently.

**Security:** Do not print or publish the secret value while troubleshooting.

---

# 18. Troubleshooting Summary

| No. | Issue                                          | Main Area to Check                                    |
| --- | ---------------------------------------------- | ----------------------------------------------------- |
| 1   | Python environment and dependency installation | Python, pip, Boto3, Watchdog                          |
| 2   | Watchdog folder monitoring                     | Local folder path and event handlers                  |
| 3   | Duplicate uploads                              | Created and modified events                           |
| 4   | Task Scheduler automation                      | Task trigger, Python path, working directory          |
| 5   | AWS CLI authentication                         | Credentials and IAM identity                          |
| 6   | Local file not appearing in S3                 | Bucket name, upload permissions, script configuration |
| 7   | Missing S3 VPC endpoint                        | VPC endpoint and route table association              |
| 8   | VPC DNS configuration                          | DNS support and DNS hostnames                         |
| 9   | Lambda missing AWS permissions                 | Execution role and permission policies                |
| 10  | PyMySQL import or layer issue                  | ZIP structure, runtime, architecture, layer ARN       |
| 11  | Lambda timeout during Secrets Manager access   | Network connectivity and timeout                      |
| 12  | MySQL error 1044                               | Database selection and database privileges            |
| 13  | RDS insert failure                             | Table, SQL, columns, privileges, transaction          |
| 14  | S3 file retrieval and parsing                  | Event payload, object key, CSV processing             |
| 15  | Incorrect Lambda processing sequence           | Application logic and dependency order                |
| 16  | SNS notification failure                       | Topic ARN, region, IAM permissions                    |
| 17  | S3 event not triggering Lambda                 | Notification configuration and invoke permission      |
| 18  | SQS event processing failure                   | Queue policy, event source mapping, payload structure |
| 19  | Lambda-to-RDS connection failure               | VPC, routes, security groups, endpoint                |
| 20  | Secrets Manager authentication issues          | Secret fields, credentials, database privileges       |

---

# 19. Final Lessons Learned

The major lessons from this project were:

1. Local folder monitoring and AWS event processing are separate stages and should be tested independently.
2. AWS CLI authentication does not automatically grant every required service permission.
3. Lambda execution roles need explicit permissions for the services and operations used by the application.
4. IAM permissions, VPC networking, and MySQL database privileges are separate layers of access control.
5. An S3 VPC endpoint is required only when the intended network design needs it; it does not replace IAM or bucket permissions.
6. VPC DNS settings must be checked when service endpoint resolution is part of the problem.
7. A custom Lambda Layer must have the correct ZIP structure and compatible runtime and architecture.
8. Secrets Manager access and RDS database access should be diagnosed independently.
9. MySQL error 1044 indicates a database privilege problem; the database name and grants must both be checked.
10. The Lambda function must retrieve the S3 object, validate the data, and map the fields correctly before inserting records.
11. SNS publishing requires appropriate permissions and the correct topic configuration.
12. SQS-based processing requires a different event payload structure from direct S3-to-Lambda processing.
13. CloudWatch logs are essential for identifying failures at each stage.
14. End-to-end testing should verify the complete path from the local file to the final database record and notification.

## Conclusion

This troubleshooting guide documents the key technical challenges associated with implementing the real-time event-driven data ingestion pipeline.

It can be used as a project reference, deployment troubleshooting guide, and interview preparation document for explaining the problems encountered, their root causes, and the corrective actions taken.
