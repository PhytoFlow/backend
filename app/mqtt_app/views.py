import paho.mqtt.client as mqtt
from django.http import JsonResponse
from .tasks import upload_to_s3

def on_connect(client, userdata, flags, rc):
    print(f"Conectado ao MQTT Broker com código {rc}")
    client.subscribe("topico/exemplo")

def on_message(client, userdata, msg):
    print(f"Mensagem recebida: {msg.payload.decode()}")
    # Aqui você pode processar a mensagem ou chamar uma tarefa assíncrona
    upload_to_s3.delay(msg.payload.decode())

def mqtt_view(request):
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_BROKER_URL, MQTT_BROKER_PORT, 60)
    client.loop_start()
    return JsonResponse({"status": "Conectado ao MQTT"})