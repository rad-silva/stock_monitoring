'''
Fornecedor:
- Possui estoque de peças ilimitado
- Consideraremos que está localizado a uma faixa aleatória de distância em metros do almoxarifado
- Fica a critério do monitor checar o nível de estoque no almoxarifado e solicitar peças aos fornecedores
- Pode entregar uma ou mais peças de uma vez
'''


from utils import *
import paho.mqtt.client as mqtt
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
    payload = msg.payload.decode("utf-8")
    code, data = payload.split(':')
    
    # recebeu uma mensagem de solicitação de reposição vinda do almoxarifado/monitor
    if code == str(sf_code):
      part_index, quantidade = data.split(",")
      part_index = int(part_index)
      quantidade = int(quantidade)

      # Considera um tempo de entrega
      time.sleep(random.randint(1,10))

      # envia resposta de entrega
      self.client.publish(topic_estoque, f"{rf_code}:{part_index},{quantidade}") 
      print(f" - envio de peça {part_index}, quantidade {quantidade}")

    
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
