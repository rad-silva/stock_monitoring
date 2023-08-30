'''
Fornecedor:
- Possui estoque de peças ilimitado
- Consideraremos que está localizado a uma faixa aleatória de distância em metros do almoxarifado
- Fica a critério do monitor checar o nível de estoque no almoxarifado e solicitar peças aos fornecedores
- Pode entregar uma ou mais peças de uma vez
'''


from utils import *
import paho.mqtt.client as mqtt
import json
import time


class Fornecedor:
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
    data_json = msg.payload.decode("utf-8")
    remetente, destinatario, code, part_index, quantidade = json.loads(data_json)

    # recebeu uma mensagem de solicitação de reposição vinda do almoxarifado/monitor
    if code == sf_code:
      # Considera um tempo de entrega
      time.sleep(random.randint(1,2))

      # envia resposta de entrega
      data = json.dumps((self.name, "almoxarifado", rf_code, part_index, quantidade))
      self.client.publish(topic_estoque, data)

      print(f"reposição peça {part_index}, quantidade {quantidade}")
      
    
  def start(self):
    try:
      self.client.loop_forever()
    except KeyboardInterrupt:
      self.client.loop_stop()
      self.client.disconnect()
      print(f"\nconexão {self.name} encerrada!")


#
# Inicializa objeto do fornecedor
fornecedor = Fornecedor("fornecedor")
fornecedor.start()
