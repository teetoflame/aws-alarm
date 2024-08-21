import json
import boto3
from datetime import datetime

def lambda_handler(event, context):
    # Initialize AWS clients
    budgets_client = boto3.client('budgets')
    sns_client = boto3.client('sns')
    
    # Define parameters
    account_id = '905418229104'  # Replace with your AWS account ID
    budget_name = 'MyDailyBudget9'  # Replace with your budget name
    sns_topic_arn = 'arn:aws:sns:eu-north-1:905418229104:BudgetNotificationTopic9'  # Replace with your SNS Topic ARN
    
    # Retrieve the budget
    try:
        response = budgets_client.describe_budget(
            AccountId=account_id,
            BudgetName=budget_name
        )
        budget_details = response['Budget']
        
        # Format the budget data for the report
        report = {
            "BudgetName": budget_details['BudgetName'],
            "BudgetLimit": budget_details['BudgetLimit'],
            "CostFilters": budget_details.get('CostFilters', {}),
            "CostTypes": budget_details.get('CostTypes', {})
        }
        
        # Convert report to string
        report_str = json.dumps(report, indent=2)
        
        # Send the report via SNS
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
