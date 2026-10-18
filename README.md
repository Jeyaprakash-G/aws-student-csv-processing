# ☁️ AWS Student CSV Processing Automation

### 🚀 Python Automation | Amazon S3 | AWS Lambda | RDS MySQL | SNS

This project automates the process of uploading student CSV files from a local Windows machine to AWS, processing the files with AWS Lambda, and interacting with an Amazon RDS MySQL database.

The solution uses **Python, Boto3, Watchdog, Amazon S3, AWS Lambda, AWS Secrets Manager, Amazon RDS, and Amazon SNS** to demonstrate event-driven automation and cloud service integration.

---

# 🚀 Project Overview

The workflow monitors a local folder for new CSV files, uploads them to Amazon S3, and uses an S3 event to invoke AWS Lambda. Lambda processes the file, retrieves database credentials securely from AWS Secrets Manager, and connects to Amazon RDS for MySQL.

### 🎯 Project Objectives

* 📂 Automatically upload CSV files from a local Windows folder to Amazon S3
* 👀 Monitor local folder activity using Python Watchdog
* 🔄 Use Boto3 to interact with AWS services
* ⚡ Trigger AWS Lambda when a new object is created in S3
* 🔐 Retrieve database credentials securely from AWS Secrets Manager
* 🗄️ Process student records using Amazon RDS for MySQL
* 📧 Send processing notifications using Amazon SNS
* 📊 Monitor execution and errors using Amazon CloudWatch Logs

---

# 🏗️ Architecture & End-to-End Flow

```text
                  Local Windows Machine
                           |
                           v
                Python Script (Watchdog)
                     + Boto3 SDK
                           |
                           v
                    Amazon S3 Bucket
                           |
                           v
                 S3 ObjectCreated Event
                           |
                           v
                     AWS Lambda
                           |
                 +---------+----------+
                 |                    |
                 v                    v
         AWS Secrets Manager    Amazon RDS MySQL
         (DB credentials)       (Student records)
                                      |
                                      v
                             Processing verification
                                      |
                                      v
                                  Amazon SNS
                                      |
                                      v
                               Email notification
```

**Workflow summary:**

1. A CSV file is added to the monitored folder on the Windows machine.
2. The Python Watchdog script detects the file.
3. Boto3 uploads the file to the S3 bucket.
4. The S3 `ObjectCreated` event invokes the Lambda function.
5. Lambda retrieves database credentials from Secrets Manager.
6. Lambda connects to RDS MySQL and processes or verifies student records.
7. Notifications are sent through SNS according to the implemented configuration.
8. CloudWatch Logs are used to review execution results and errors.

---

# 🛠️ Technologies & AWS Services

| Category | Technology / Service | Purpose |
|---|---|---|
| Scripting | Python | Local automation and Lambda logic |
| AWS SDK | Boto3 | Access AWS services from Python |
| Folder monitoring | Watchdog | Detect new local files |
| Local scheduling | Windows Task Scheduler | Start the monitoring script automatically |
| Object storage | Amazon S3 | Store CSV files |
| Event-driven processing | S3 Event Notifications | Trigger Lambda after an upload |
| Serverless compute | AWS Lambda | Process uploaded CSV files |
| Database | Amazon RDS for MySQL | Store student records |
| Credentials | AWS Secrets Manager | Securely store database credentials |
| Notifications | Amazon SNS | Send success/failure notifications |
| Monitoring | Amazon CloudWatch Logs | Troubleshoot Lambda executions |
| Permissions | AWS IAM | Control service access |
| Networking | Amazon VPC, Security Groups, VPC Endpoints | Control network access and service connectivity |
| Lambda dependency | PyMySQL Layer | Provide the MySQL client library |

---

# 📂 Project Implementation

## 🔹 Phase 1 — Local Machine to Amazon S3

* Configured AWS CLI on the Windows machine.
* Installed the required Python packages.
* Created a local folder for CSV files.
* Developed a Python script using Watchdog and Boto3.
* Configured the script to upload new files to Amazon S3.
* Used Windows Task Scheduler to start the script automatically, where configured.
* Verified that files were uploaded to the expected S3 location.

## 🔹 Phase 2 — Amazon S3 to AWS Lambda

* Created the S3 bucket.
* Configured an S3 `ObjectCreated` event notification.
* Connected the event notification to the Lambda function.
* Configured the Lambda execution role and required permissions.
* Implemented logic to read and process the uploaded CSV file.
* Used CloudWatch Logs to inspect execution results.

## 🔹 Phase 3 — AWS Lambda to Amazon RDS MySQL

* Created an Amazon RDS for MySQL database.
* Created the application database and `students` table.
* Stored database credentials in AWS Secrets Manager.
* Configured Lambda environment variables.
* Added the PyMySQL dependency through a compatible Lambda Layer.
* Configured Lambda and RDS VPC networking.
* Allowed MySQL traffic on TCP port `3306` from the Lambda security group to the RDS security group.
* Verified student records in the database.

## 🔹 Phase 4 — Notifications & Monitoring

* Created SNS topics for success and failure notifications.
* Configured email subscriptions as required.
* Configured the permissions and network connectivity needed for publishing to SNS.
* Used CloudWatch Logs to troubleshoot Lambda execution.
* Tested the processing workflow and reviewed the resulting status.

---

# ☁️ AWS Resources Used

The following names were used during the practice project. Verify them before publishing or sharing the repository.

| AWS Resource | Name / Details |
|---|---|
| Region | `ap-south-1` — Mumbai |
| Amazon S3 bucket | `student-csv-ingestion-jp` |
| S3 object prefix | `uploads/` |
| AWS Lambda function | `devops-rds-lambda-connection` |
| RDS application database | `studentdb` |
| MySQL table | `students` |
| SNS success topic | `student-csv-processing-topic` |
| SNS failure topic | `student-csv-failure` |
| SQS queue | `student-csv-processing-queue` |
| CloudWatch log group | `/aws/lambda/devops-rds-lambda-connection` |

> **Note:** The SQS queue was also part of the practice resources. Include it in the active processing architecture only if it is actually connected to and used by the workflow.

---

# 🔐 Security & Networking

* 🔑 Used IAM roles and policies to control access to AWS resources.
* 🪣 Kept the S3 bucket private and Block Public Access enabled.
* 🔒 Stored database credentials in AWS Secrets Manager instead of hardcoding them in the application.
* 🛡️ Configured the RDS security group to allow database access from the Lambda security group.
* 🌐 Configured VPC networking and required service endpoints or routing.
* 🔍 Reviewed CloudWatch Logs when troubleshooting service connectivity.

**GitHub security checklist:**

* Never upload AWS access keys or secret access keys.
* Never commit database passwords or actual Secrets Manager values.
* Do not upload `.env` files or private key files such as `.pem`.
* Do not publish real student personal data.
* Remove credentials and sensitive information from code, logs, and screenshots before committing.

---

# 📦 Python Dependencies

For the local folder-monitoring script, create a `requirements.txt` file containing:

```text
boto3
watchdog
```

Install the dependencies with:

```bash
python -m pip install -r requirements.txt
```

The Lambda function uses **PyMySQL** as the MySQL client library. If using a Lambda Layer, ensure that it is compatible with the selected Python runtime and CPU architecture.

---

# 🧪 Testing & Validation

The following checks can be used to validate the workflow:

- [ ] AWS CLI access works from the local machine.
- [ ] The Python folder-monitoring script starts successfully.
- [ ] A new CSV file is uploaded to the S3 `uploads/` prefix.
- [ ] The S3 event invokes the expected Lambda function.
- [ ] Lambda reads the uploaded object successfully.
- [ ] Lambda retrieves the database credentials from Secrets Manager.
- [ ] Lambda connects to RDS MySQL.
- [ ] Expected student records are processed and verified.
- [ ] SNS notifications behave as configured.
- [ ] CloudWatch Logs show the expected execution result.

---

# 🛠️ Troubleshooting

### ❌ RDS database access denied

* Verify the database name, username, password, secret JSON key, and database permissions.

### ❌ Lambda cannot connect to RDS

* Check the VPC, subnet configuration, security groups, routing, and TCP port `3306`.

### ❌ Lambda cannot access S3

* Verify the S3 event configuration, object key, IAM permissions, and required endpoint or network routing.

### ❌ Secrets Manager request fails or times out

* Verify `secretsmanager:GetSecretValue`, the secret ARN, endpoint configuration, private DNS, security group rules, and routing.

### ❌ SNS connection timeout

* Check whether Lambda has network connectivity to SNS through an SNS interface VPC endpoint or an appropriate NAT/routing configuration.
* A timeout may indicate a network issue rather than an IAM permission denial.

### ❌ PyMySQL import error

* Verify the Lambda Layer structure, Python runtime compatibility, and CPU architecture.

---

# 🚀 Future Enhancements

* 🏗️ Provision AWS resources using Terraform.
* 🔄 Implement a CI/CD pipeline using GitHub and Jenkins.
* 🧪 Add automated tests and code quality checks.
* 🔐 Add security scanning using SonarQube and Trivy.
* 📊 Improve monitoring, CloudWatch alarms, and structured logging.
* 🔁 Add retry handling and duplicate-record protection.
* 📬 Use SQS for buffering and asynchronous processing if required by the design.

---

# 📁 Suggested Repository Structure

```text
aws-student-csv-processing/
├── README.md
├── upload_to_s3.py
├── requirements.txt
├── .gitignore
├── lambda/
│   └── lambda_function.py
└── docs/
    ├── architecture.png
    └── troubleshooting.md
```

Add only files that exist in your project. Do not commit credentials or sensitive data.

---

# 🎯 Project Summary

This project demonstrates an event-driven AWS workflow that automates CSV file ingestion from a local Windows machine into Amazon S3, invokes AWS Lambda for processing, integrates with Amazon RDS for MySQL, retrieves credentials securely through AWS Secrets Manager, and supports notifications through Amazon SNS.

It provides hands-on practice with **Python automation, serverless computing, cloud storage, database integration, IAM, VPC networking, and CloudWatch monitoring**.

---

## ⭐ Learn • Practice • Automate • Deploy • Monitor • Improve 🚀

