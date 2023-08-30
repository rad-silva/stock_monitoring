'''
Almoxarifado:
- Um armazém com estoque para reposição de peças nas fábricas 
- Consideraremos que está localizado a 600 metros da fábrica
- Fica a critério do monitor estimar o uso de peças e solicitar reabastecimento na fábrica
- Fica a critério do monitor checar o nível de estoque no almoxarifado e solicitar peças aos fornecedores
'''


from utils import *
import paho.mqtt.client as mqtt
import json
import time


class testador:
  def __init__(self, name):
    self.name = name
    self.client = mqtt.Client(self.name)
    self.client.on_connect = self.on_connect
    self.client.on_message = self.on_message
    self.client.connect("localhost", 1883, 60)


  def on_connect(self, client, userdata, flags, rc):
    print(f"{self.name} conectado ao broker")
    self.client.subscribe(topic_monitor)


  def on_message(self, client, userdata, msg):
    print("opa")


  def send_data(self):
    while(True):
      time.sleep(6)

      estoque_data = [
        [100, 75, 80, 50, 70, 60, 50],
        [50, 25, 10, 50, 4, 8, 30],
        ['green', 'yellow', 'green', 'red', 'red', 'red', 'green']
      ]
      print(estoque_data)

      data = json.dumps(estoque_data)
      self.client.publish(topic_dashboard, data)

      time.sleep(6)

      estoque_data = [
        [100, 75, 80, 50, 70, 60, 50],
        [50, 75, 80, 50, 70, 60, 50],
        ['green', 'green', 'green', 'green', 'green', 'green', 'green']
      ]
      print(estoque_data)

      data = json.dumps(estoque_data)
      self.client.publish(topic_dashboard, data)

      time.sleep(6)

      estoque_data = [
        [100, 75, 80, 50, 70, 60, 50],
        [10, 10, 10, 10, 4, 8, 30],
        ['red', 'red', 'red', 'red', 'red', 'red', 'red']
      ]
      print(estoque_data)

      data = json.dumps(estoque_data)
      self.client.publish(topic_dashboard, data)

      time.sleep(6)

    
  def start(self):
    try:
      self.client.loop_start() # inicia um loop MQTT em uma thread separada
      self.send_data()   # mantém a execução da próxima parte do programa
    except KeyboardInterrupt:
      self.client.loop_stop()
      self.client.disconnect()
      print(f"\nconexão {self.name} encerrada!")


#
# Inicializa objeto do Almoxarifado
send = testador("fuck")
send.start()
