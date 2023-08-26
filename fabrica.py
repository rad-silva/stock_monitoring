'''
Fábrica:
- Fabricação empurrada -> 1 tipo de equipamento é montado apesar das demandas
- 1 linha de produção (uma thread) tem um buffer (estoque) de peças que será decrementado
  conforme o uso no processo de montagem do esquipamento
- Cada linha de produção é especializada em montar um produto
- Cada linha de porudção deve fabricar 48 produtos 
- O estoque local de cada linha deve ser mantido atualizado no dashboard
- Fica a critério do dashboard estimar o uso de peças e solicitar reabastecimento
- Se faltar pessa, toda a linha de produção para e um timer é iniciado para relatar o tempo ocioso
- A fábrica trabalha durante 16 horas
- Utilizamos os minutos dividido por 60 para fins de testes, ou seja, 1min = 1seg na aplicação
'''

from utils import *
import paho.mqtt.client as mqtt
import time
import sys

class LinhaProducao:
  def __init__(self, name, client):
    self.name = name
    self.client = client
    self.estoque = [10] * num_pecas

  
  def action_part(self, part_index):
    self.estoque[part_index] -= 1
    self.client.publish(topic_estoque, f"{ds_code}:{part_index}") 

    # considera o tempo de montagem da peça
    time.sleep(timer[part_index])


  def product_assembly(self, prod_name, produto, quantidade):
    for p in range(quantidade):
      print(f"Montagem do produto {prod_name}: ({p}/{quantidade})")
      # print("estoque:", [f"{value:02}" for value in estoque_pecas])
      # print("lista:  ", [f"{value:02}" for value in produto], "\n")

      for part_index in range(num_pecas): 

        # verfica se a peça 'part_index' é utilizada nesse produto
        if (produto[part_index] != 0):
          print(f"- montagem da peça {part_index} ({produto[part_index]} un): ", end="")
          qt_parte = produto[part_index]

          for _ in range(qt_parte):
            if (self.estoque[part_index] <= 0):
              print(f"\nFALTA DE PEÇA: {part_index} -> LINHA DE PRODUÇÃO PARADA...")
              while (self.estoque[part_index] <= 0):
                pass
            
            # else:
            self.action_part(part_index)
            print("#", end="")
            sys.stdout.flush() 

          print()

    return quantidade


class Fabrica:
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
    
    if code == str(ra_code):
      part_index, quantidade = data.split(',')
      part_index = int(part_index)
      quantidade = int(quantidade)

      # atualiza os dados de estoque  da fábrica
      self.linha1.estoque[part_index] += quantidade

      print(f'\n>> Recebido reposição: peça {part_index}, quantidade {quantidade}\n')


  def administration(self):
    total_produtos = 10
    produtos_fabricados = 0

    self.linha1 = LinhaProducao("l1", self.client)

    while produtos_fabricados < total_produtos:
      produtos_fabricados += self.linha1.product_assembly("pv1", pv1, total_produtos)

    print("\nProducao concluída!")
    return

    
  def start(self):
    try:
      self.client.loop_start()
      self.administration()
    except KeyboardInterrupt:
      self.client.loop_stop()
      self.client.disconnect()
      print(f"\nconexão {self.name} encerrada!")


#
# Inicializa objeto do fabrica
fabrica = Fabrica("fabrica")
fabrica.start()
