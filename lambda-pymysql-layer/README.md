# AWS Lambda PyMySQL Layer

## Project Overview

This project demonstrates how to create a custom AWS Lambda Layer containing the PyMySQL Python library for connecting AWS Lambda functions to Amazon RDS MySQL.

Instead of including the PyMySQL library directly in the Lambda function code, we package it separately as a Lambda Layer and attach it to the function.

## Layer Configuration

| Property           | Value                                |
| ------------------ | ------------------------------------ |
| Layer Name         | `devops-pymysql-layer`               |
| Python Library     | PyMySQL                              |
| Library Version    | 1.2.3                                |
| Compatible Runtime | Python 3.14                          |
| Architecture       | ARM64                                |
| AWS Region         | Asia Pacific (Mumbai) — `ap-south-1` |

## Repository Structure

```text
aws-lambda-pymysql-layer/
├── README.md
├── create_layer.ps1
└── requirements.txt
```

## Prerequisites

* AWS account
* Python installed on the local system
* Python package installer (`pip`)
* AWS Lambda access
* Windows PowerShell

## Step 1: Create the Layer Package

The `create_layer.ps1` PowerShell script automates the following tasks:

1. Creates the required Python directory.
2. Installs PyMySQL version 1.2.3.
3. Packages the library into a ZIP file.

Run the script using PowerShell:

```powershell
.\create_layer.ps1
```

The script creates the ZIP package at:

```text
C:\lambda-rds-project\devops-pymysql-layer.zip
```

Ensure that the directory structure inside the ZIP begins with the `python/` folder.

## Step 2: Create the AWS Lambda Layer

1. Sign in to the AWS Management Console.
2. Open AWS Lambda in the Mumbai region (`ap-south-1`).
3. Select **Layers** from the left navigation menu.
4. Click **Create layer**.
5. Enter `devops-pymysql-layer` as the layer name.
6. Upload `devops-pymysql-layer.zip`.
7. Select Python 3.14 as the compatible runtime.
8. Select ARM64 as the compatible architecture.
9. Click **Create**.

## Step 3: Attach the Layer to a Lambda Function

1. Open your Lambda function in the AWS Console.
2. Scroll to the **Layers** section.
3. Click **Add a layer**.
4. Select **Custom layers**.
5. Choose `devops-pymysql-layer`.
6. Select version 1.
7. Click **Add**.

The PyMySQL library is now available to the Lambda function through the attached layer.

## Step 4: Use PyMySQL in Lambda

Import the library in your Lambda Python code:

```python
import pymysql
```

The function can use PyMySQL to establish a connection to Amazon RDS for MySQL, provided that the network configuration, credentials, and permissions are correct.

## Dependencies

The `requirements.txt` file contains:

```text
PyMySQL==1.2.3
```

## Important Notes

* The ZIP package must contain a top-level `python/` directory.
* The Lambda runtime and architecture must be compatible with the layer.
* The Lambda function requires appropriate network connectivity to access RDS.
* Database credentials should be stored securely, for example, in AWS Secrets Manager.
* Do not store database passwords, AWS access keys, or other secrets in this repository.

## Project Outcome

Successfully created a reusable AWS Lambda Layer containing PyMySQL and attached it to a Lambda function to support connectivity with Amazon RDS MySQL.
