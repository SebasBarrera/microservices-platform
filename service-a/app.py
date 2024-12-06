import boto3
import time
import uuid
import json

sns_client = boto3.client('sns', region_name='us-east-1')

sns_topic_arn = 'arn:aws:sns:us-east-1:851725303021:HeartbeatTopic'

lamport_clock = 0

def send_heartbeat():
    message = {
        'ServiceID': 'ServiceA',
        'Timestamp': int(time.time()),
        'MessageID': str(uuid.uuid4()),
        'LamportClock': lamport_clock
    }
    sns_client.publish(
        TopicArn=sns_topic_arn,
        Message=json.dumps(message)
    )
    print("Heartbeat sent:", message)

def send_event():
    global lamport_clock
    lamport_clock += 1
    event_message = {
        'ServiceID': 'ServiceA',
        'EventID': str(uuid.uuid4()),
        'LamportClock': lamport_clock,
        'Data': 'Evento de prueba',
        'SendTimestamp': int(time.time() * 1000)
    }
    sns_client.publish(
        TopicArn=sns_topic_arn,
        Message=json.dumps(event_message)
    )
    print("Event sent:", event_message)

if __name__ == '__main__':
    while True:
        send_heartbeat()
        send_event()
        time.sleep(60)
