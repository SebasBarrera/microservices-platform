import json

def lambda_handler(event, context):
    try:
        # Procesa cada registro en el evento
        for record in event['Records']:
            sns_message = record['Sns']
            message_body = sns_message['Message']
            
            # Deserializa el JSON dentro de 'Message'
            message = json.loads(message_body)
            
            # Ahora puedes acceder a los campos del mensaje
            service_id = message['ServiceID']
            event_id = message['EventID']
            timestamp = message['Timestamp']
            lamport_clock = message['LamportClock']
            data = message['Data']
            
            print(f"Mensaje procesado: ServiceID={service_id}, EventID={event_id}, Timestamp={timestamp}, LamportClock={lamport_clock}, Data={data}")
        
        return {
            'statusCode': 200,
            'body': json.dumps('Mensaje procesado exitosamente')
        }
    
    except KeyError as e:
        print(f"KeyError: {str(e)}")
        return {
            'statusCode': 400,
            'body': json.dumps(f"Error en los datos del mensaje: {str(e)}")
        }
    except Exception as e:
        print(f"Error inesperado: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error interno: {str(e)}")
        }
