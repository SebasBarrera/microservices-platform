import json
import boto3

def lambda_handler(event, context):
    cloudwatch = boto3.client('cloudwatch')
    for record in event['Records']:
        message = json.loads(record['Sns']['Message'])
        service_id = message['ServiceID']
        timestamp = message['Timestamp']
        cloudwatch.put_metric_data(
            Namespace='Microservices',
            MetricData=[
                {
                    'MetricName': 'Heartbeat',
                    'Dimensions': [
                        {
                            'Name': 'ServiceID',
                            'Value': service_id
                        },
                    ],
                    'Timestamp': timestamp,
                    'Value': 1
                },
            ]
        )
        print(f"Heartbeat processed for {service_id} at {timestamp}")
