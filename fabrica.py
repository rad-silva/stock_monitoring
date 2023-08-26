'''
Fábrica:
- Fabricação empurrada -> 1 tipo de equipamento é montado apesar das demandas
- 1 linha de produção (uma thread) tem um buffer (estoque) de peças que será decrementado
  conforme o uso no processo de montagem do esquipamento
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
    '''
    Implementar o reabastecimento de peças para estoque local vindo do amoxarife
    ideias até agora: 
      - o almoxarife vai enviar para o monitor uma lista de itens que entregou
        e o monitor vai repassar essa lista pra fabrica
        a fabrica deve atualizar as informações de estoque da linha de produção
        deve manter as informações local da fabrica e do monitor sincronizadas ja que ele deve saber o nivel de estoque
      - o almoxarife vai enviar para o monitor uma lista de itens que entregou
        e o monitor deve atualizar as informaçoes de estoque que ele tem sobre a linha de produção
        seria como se a fábrica em si utiliza-se os (e confiasse nos) dados mantidos pelo monitor
    '''

    payload = msg.payload.decode("utf-8")
    code, data = payload.split(':')
    
    if code == str(ra_code):
      part_index, quantidade = data.split(',')
      part_index = int(part_index)
      quantidade = int(quantidade)

      # atualiza os dados de estoque  da fábrica
      estoque_pecas[part_index] += quantidade

      print(f'\n>> Recebido reposição: peça {part_index}, quantidade {quantidade}\n')


  '''
  Função dedicada às ações de montagem de cada peça em um produto.
  Considera-se que o operador indique a utilização de uma peça (dar baixa no estoque)
  e utilize algum tempo para sua montagem no produto.
  '''
  def action_part(self, part_index):
    estoque_pecas[part_index] -= 1
    self.client.publish(topic_estoque, f"{ds_code}:{part_index}") 

    # considera o tempo de montagem da peça
    time.sleep(timer[part_index])

  
  def production_line(self):
    while True:
      print("estoque:", [f"{value:02}" for value in estoque_pecas])
      print("lista:  ", [f"{value:02}" for value in produto], "\n")
      print("iniciando montagem do produto 1")

      for i in range(len(produto)):
        if (produto[i] != 0):
          print(f"- montagem da peça {i} ({produto[i]} un): ", end="")

          for _ in range(produto[i]):
            if (estoque_pecas[i] <= 0):
              print(f"\n\nFALTA DE PEÇA: {i} -> LINHA DE PRODUÇÃO PARADA...")
              while (estoque_pecas[i] <= 0):
                pass
            
            # else:
            self.action_part(i)
            print("#", end="")
            sys.stdout.flush() 

          print()

    
  def start(self):
    try:
      self.client.loop_start()
      self.production_line()
    except KeyboardInterrupt:
      self.client.loop_stop()
      self.client.disconnect()
      print(f"\nconexão {self.name} encerrada!")


#
# Inicializa objeto do fabrica
fabrica = Fabrica("fabrica")
fabrica.start()
