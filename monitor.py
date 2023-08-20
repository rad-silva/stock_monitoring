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
    client.subscribe(topic_estoque)  # Se inscreve no tópico para receber números

def on_message(client, userdata, msg):
    received_number = msg.payload
    print(received_number)
    #client.publish(topic_monitor, str(multiplied_number))  # Publica o número multiplicado

if __name__ == "__main__":
    client = mqtt.Client("monitor")
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect("localhost", 1883, 60)
    client.loop_forever()
