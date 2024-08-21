---

# Daily Budget Report Setup Guide

This guide details the steps to set up a daily AWS budget report that is triggered by a Lambda function and sends notifications to an SNS topic.

## Prerequisites

- AWS CLI installed and configured
- IAM permissions for creating roles, policies, Lambda functions, SNS topics, and budgets
- An existing AWS account

## Setup Steps

### 1. Create IAM Role for Lambda

Create an IAM role with necessary permissions for Lambda execution.

**Create Role:**
```bash
aws iam create-role --role-name LambdaExecutionRole9 --assume-role-policy-document file://trust-policy.json
```

**Trust Policy (`trust-policy.json`):**
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

**Attach Policies:**
```bash
aws iam attach-role-policy --role-name LambdaExecutionRole9 --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
aws iam attach-role-policy --role-name LambdaExecutionRole9 --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaRole
```

### 2. Create AWS Budget

**Set Up Budget:**
```bash
aws budgets create-budget --account-id YOUR_ACCOUNT_ID --budget-name MyDailyBudget9 --budget-type COST --time-unit DAILY --budget-limit Amount=300,Unit=USD
```

### 3. Create SNS Topics and Subscriptions

**Create SNS Topic:**
```bash
aws sns create-topic --name BudgetNotificationTopic9
```

**Subscribe to SNS Topic:**
```bash
aws sns subscribe --topic-arn arn:aws:sns:YOUR_REGION:YOUR_ACCOUNT_ID:BudgetNotificationTopic9 --protocol email --notification-endpoint your-email@example.com
```

### 4. Write and Package Lambda Function Code

**Lambda Function Code (`index.py`):**
```python
import json
import boto3

def lambda_handler(event, context):
    budgets_client = boto3.client('budgets')
    sns_client = boto3.client('sns')
    
    account_id = 'YOUR_ACCOUNT_ID'
    budget_name = 'MyDailyBudget9'
    sns_topic_arn = 'arn:aws:sns:YOUR_REGION:YOUR_ACCOUNT_ID:BudgetNotificationTopic9'
    
    try:
        response = budgets_client.describe_budget(AccountId=account_id, BudgetName=budget_name)
        budget_details = response['Budget']
        
        report = {
            "BudgetName": budget_details['BudgetName'],
            "BudgetLimit": budget_details['BudgetLimit']
        }
        
        report_str = json.dumps(report, indent=2)
        
        sns_client.publish(
            TopicArn=sns_topic_arn,
            Subject='Daily Budget Report',
            Message=report_str
        )
        
        return {
            "statusCode": 200,
            "body": json.dumps("Daily budget report sent.")
        }
    
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps(f"Error: {str(e)}")
        }
```

**Create Deployment Package:**
```bash
mkdir lambda_function
cd lambda_function
echo 'import json\n\ndef lambda_handler(event, context):\n    return {\n        "statusCode": 200,\n        "body": json.dumps("Daily budget report generated.")\n    }' > index.py
zip function.zip index.py
```

**Create Lambda Function:**
```bash
aws lambda create-function --function-name DailyBudgetReportFunction9 --runtime python3.8 --role arn:aws:iam::YOUR_ACCOUNT_ID:role/LambdaExecutionRole9 --handler index.lambda_handler --zip-file fileb://function.zip
```

### 5. Create CloudWatch Events Rule

**Create Rule:**
```bash
aws events put-rule --name DailyEventRule9 --schedule-expression 'rate(1 day)'
```

**Add Target to Rule:**
```bash
aws events put-targets --rule DailyEventRule9 --targets Id=1,Arn=arn:aws:lambda:YOUR_REGION:YOUR_ACCOUNT_ID:function:DailyBudgetReportFunction9
```

**Grant Permission to CloudWatch Events:**
```bash
aws lambda add-permission --function-name DailyBudgetReportFunction9 --principal events.amazonaws.com --statement-id DailyEventRule9Permission --action lambda:InvokeFunction --source-arn arn:aws:events:YOUR_REGION:YOUR_ACCOUNT_ID:rule/DailyEventRule9
```

### 6. Create CloudFormation Template

**Define Resources in `cloudformation-template.yaml`:**
```yaml
AWSTemplateFormatVersion: '2010-09-09'
Resources:
  BudgetNotificationTopic9:
    Type: AWS::SNS::Topic
    Properties:
      DisplayName: Budget Notification Topic

  BudgetSubscriptionEmail1:
    Type: AWS::SNS::Subscription
    Properties:
      TopicArn: !Ref BudgetNotificationTopic9
      Protocol: email
      Endpoint: your-email@example.com

  BudgetSubscriptionEmail2:
    Type: AWS::SNS::Subscription
    Properties:
      TopicArn: !Ref BudgetNotificationTopic9
      Protocol: email
      Endpoint: your-second-email@example.com

  DailyBudgetReportFunction9:
    Type: AWS::Lambda::Function
    Properties:
      FunctionName: DailyBudgetReportFunction9
      Runtime: python3.8
      Role: arn:aws:iam::YOUR_ACCOUNT_ID:role/LambdaExecutionRole9
      Handler: index.lambda_handler
      Code:
        S3Bucket: your-bucket
        S3Key: function.zip

  DailyEventRule9:
    Type: AWS::Events::Rule
    Properties:
      ScheduleExpression: rate(1 day)
      Targets:
        - Arn: !GetAtt DailyBudgetReportFunction9.Arn
          Id: "1"

  LambdaInvokePermission:
    Type: AWS::Lambda::Permission
    Properties:
      Action: lambda:InvokeFunction
      FunctionName: !Ref DailyBudgetReportFunction9
      Principal: events.amazonaws.com
      SourceArn: !GetAtt DailyEventRule9.Arn
```

**Deploy CloudFormation Stack:**
```bash
aws cloudformation create-stack --stack-name MyBudgetStack9 --template-body file://cloudformation-template.yaml
```

## Notes

- Replace placeholders like `YOUR_ACCOUNT_ID`, `YOUR_REGION`, `your-email@example.com`, and `your-bucket` with actual values.
- Confirm SNS subscriptions from the provided email addresses.

---
