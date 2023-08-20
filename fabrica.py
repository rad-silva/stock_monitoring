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
import sys
import time


def on_connect(client, userdata, flags, rc):
  client.subscribe(topic_monitor)

def on_message(client, userdata, msg):
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
  # received_result = int(msg.payload)
  # print(f"Resultado recebido: {received_result}")


'''
 Função dedicada às ações de montagem de cada peça em um produto.
 Considera-se que o operador indique a utilização de uma peça (dar baixa no estoque)
 e utilize algum tempo para sua montagem no produto.
'''
def action_part(client, part_index):
  estoque_pecas[part_index] -= 1
  client.publish(topic_estoque, f"dc:{part_index}") 

  # considera o tempo de montagem da peça
  time.sleep(timer[part_index])
  


def production_line(client):
  try:
    while True:
      print()
      print("estoque:", [f"{value:02}" for value in estoque_pecas])
      print("lista:  ", [f"{value:02}" for value in produto])
      print()
      print("iniciando montagem do produto 1")

      for i in range(len(produto)):
        if (produto[i] != 0):
          print(f"- montagem da peça {i} ({produto[i]} un): ", end="")

          for _ in range(produto[i]):
            if (estoque_pecas[i] <= 0):
              print(f"\n\nFALTA DE PEÇA: {i}")
              print("LINHA DE PRODUÇÃO PARADA...")
              while(estoque_pecas[i] <= 0):
                pass
            
            else:
              action_part(client, i)
              print("#", end="")
              sys.stdout.flush() 

          print()

  except KeyboardInterrupt:
    print("\nEncerrando a linha de produção...")
    client.loop_stop()
    client.disconnect()
  


if __name__ == "__main__":
  client = mqtt.Client("fabrica1")

  client.on_connect = on_connect
  client.on_message = on_message

  client.connect("localhost", 1883, 60)
  client.loop_start()

  production_line(client)

 
