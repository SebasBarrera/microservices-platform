# service-b/app.py

import boto3
import json
import time
import uuid

from aws_xray_sdk.core import xray_recorder, patch_all

patch_all()
xray_recorder.configure(service='ServiceB')

sqs_client = boto3.client('sqs', region_name='us-east-1')
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

idempotency_table = dynamodb.Table('IdempotencyTable')
versioned_table = dynamodb.Table('VersionedState')
write_ahead_log_table = dynamodb.Table('WriteAheadLog')

queue_url = 'https://sqs.us-east-1.amazonaws.com/851725303021/ServiceBQueue'

lamport_clock = 0

def receive_messages():
    global lamport_clock
    response = sqs_client.receive_message(
        QueueUrl=queue_url,
        MaxNumberOfMessages=10,
        WaitTimeSeconds=5
    )
    messages = response.get('Messages', [])
    for message in messages:
        body = json.loads(message['Body'])
        sns_message = json.loads(body['Message'])
        event_id = sns_message.get('EventID')
        if event_id:
            # Idempotent Receiver
            resp_idem = idempotency_table.get_item(Key={'RequestID': event_id})
            if 'Item' in resp_idem:
                print("Evento ya procesado:", event_id)
            else:
                event_clock = sns_message['LamportClock']
                lamport_clock = max(lamport_clock, event_clock) + 1
                process_event(sns_message)
                idempotency_table.put_item(
                    Item={
                        'RequestID': event_id,
                        'Timestamp': int(time.time()),
                        'Status': 'Processed'
                    }
                )

        sqs_client.delete_message(
            QueueUrl=queue_url,
            ReceiptHandle=message['ReceiptHandle']
        )

@xray_recorder.capture('process_event')
def process_event(event):
    global lamport_clock
    receive_time = int(time.time() * 1000)
    send_time = event.get('SendTimestamp')
    if send_time:
        latency = receive_time - send_time
        print(f"Latencia del evento {event['EventID']}: {latency} ms")

    write_ahead_log_table.put_item(
        Item={
            'LogID': str(uuid.uuid4()),
            'EventID': event['EventID'],
            'ServiceID': event['ServiceID'],
            'Operation': 'ProcessEvent',
            'Timestamp': receive_time
        }
    )
    print(f"Evento {event['EventID']} registrado en Write-Ahead Log")

    print("Procesando evento:", event)

    service_id = event['ServiceID']
    current_time = int(time.time())

    resp_ver = versioned_table.query(
        KeyConditionExpression=boto3.dynamodb.conditions.Key('ServiceID').eq(service_id),
        ScanIndexForward=False,
        Limit=1
    )
    if 'Items' in resp_ver and resp_ver['Items']:
        last_version = resp_ver['Items'][0]['VersionNumber']
    else:
        last_version = 0

    versioned_table.put_item(
        Item={
            'ServiceID': service_id,
            'VersionNumber': last_version + 1,
            'StateData': event['Data'],
            'Timestamp': current_time
        }
    )
    print(f"Estado versionado actualizado para {service_id} a la versión {last_version + 1}")

if __name__ == '__main__':
    while True:
        receive_messages()
        time.sleep(5)
