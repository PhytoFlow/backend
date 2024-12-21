import io
import logging
import boto3
import os
from datetime import datetime
from dotenv import load_dotenv
import paho.mqtt.client as mqtt
import json
import time
import ssl
import pandas as pd
import psycopg2


load_dotenv()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

s3 = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    aws_session_token=os.getenv('AWS_SESSION_TOKEN'),
    region_name=os.getenv('AWS_DEFAULT_REGION')
)

def list_s3_files(bucket: str, prefix: str, from_date: datetime):
    try:
        response = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)
        if "Contents" not in response:
            logger.warning(f"No files found in bucket '{bucket}' with prefix '{prefix}'.")
            return []
        return [
            item["Key"]
            for item in response["Contents"]
            if item["Key"].endswith(".parquet") and item["LastModified"] >= from_date
        ]
    except Exception as e:
        logger.error(f"Error listing files in bucket '{bucket}': {e}")
        return []
    
def read_parquet_from_s3(bucket_name, prefix, from_date):
    s3 = boto3.client('s3')
    files = list_s3_files(bucket_name, prefix, from_date)

    if not files:
        return None

    df_list = []

    for file in files:
        s3_object = s3.get_object(Bucket=bucket_name, Key=file)
        file_content = s3_object['Body'].read()

        parquet_data = io.BytesIO(file_content)
        
        df = pd.read_parquet(parquet_data)
        df_list.append(df)
        print(df)

    final_df = pd.concat(df_list, ignore_index=True)
    return final_df


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logger.info("Conectado ao broker MQTT com sucesso!")
        userdata['connected'] = True
    else:
        logger.error(f"Falha ao conectar ao broker MQTT, código de retorno: {rc}")
        userdata['connected'] = False

def create_mqtt_client(client_id, ca_certs, client_cert, client_key):
    userdata = {'connected': False}
    client = mqtt.Client(client_id, protocol=mqtt.MQTTv311, userdata=userdata)
    ssl_context = ssl.create_default_context()
    ssl_context.load_cert_chain(certfile=client_cert, keyfile=client_key)
    ssl_context.load_verify_locations(cafile=ca_certs)
    client.tls_set_context(ssl_context)
    client.on_connect = on_connect
    client.enable_logger()
    return client


def wait_for_connection(client, timeout=5):
    start_time = time.time()
    while not client._userdata['connected']:
        if time.time() - start_time > timeout:
            raise TimeoutError("Conexão com o broker MQTT expirou.")
        time.sleep(0.1)

def publish_message(client, topic, message):
    result = client.publish(topic, message)
    if result.rc == mqtt.MQTT_ERR_SUCCESS:
        logger.info(f"Mensagem publicada com sucesso no tópico {topic}. Mensagem: {message}")
    else:
        logger.error(f"Falha ao publicar mensagem, código de retorno: {result.rc}")

def send_mqtt_message(identifier, command, time_duration):
    try:
        logger.info("Tentando conectar ao broker MQTT...")

        data = {
            "identifier": identifier,
            "command": command,
            "time": time_duration,
        }
        json_data = json.dumps(data)
        logger.info(f"Payload JSON: {json_data}")

        host = "awxktv65yt674-ats.iot.us-east-1.amazonaws.com"
        port = 8883
        client_id = "irrigation-compute-000"
        ca_certs = os.getenv('CA_CERTS')
        client_cert = os.getenv('CLIENT_CERT')
        client_key = os.getenv('CLIENT_KEY')

        client = create_mqtt_client(client_id, ca_certs, client_cert, client_key)

        client.loop_start()

        client.connect(host, port)

        try:
            wait_for_connection(client)
        except TimeoutError as e:
            logger.error(f"Erro ao conectar ao broker MQTT: {e}")
            client.loop_stop()
            return

        topic = "irrigation/control/000/command"
        publish_message(client, topic, json_data)

        time.sleep(2)

    except Exception as e:
        logger.error(f"Erro ao enviar mensagem MQTT: {e}")
    finally:
        client.loop_stop()
        client.disconnect()
        logger.info("Conexão encerrada com sucesso.")
