'''
Essa aplicação utiliza a ferramenta Mosquitto https://mosquitto.org/download/ 
como broker do protocolo de mensagens MQTT
- pip install paho-mqtt

Lembre-se de ativar o Mosquitto antes de executar a aplicação
- net start mosquitto
- net stop mosquito
'''

import paho.mqtt.client as mqtt
from utils import *

def on_connect(client, userdata, flags, rc):
    print("Cliente 2 conectado ao broker")
    client.subscribe("topic/number")  # Se inscreve no tópico para receber números

def on_message(client, userdata, msg):
    received_number = int(msg.payload)
    multiplied_number = received_number * 2
    print(f"Número recebido: {received_number}, Número multiplicado: {multiplied_number}")
    client.publish("topic/result", str(multiplied_number))  # Publica o número multiplicado

client = mqtt.Client("dashboard")
client.on_connect = on_connect
client.on_message = on_message

client.connect("localhost", 1883, 60)
client.loop_forever()
