'''
Fábrica:
- Fabricação puxada -> 1 tipo de equipamento é montado apesar das demandas
- 1 linha de produção (uma thread) tem um buffer (estoque) de peças que será decrementado
  conforme o uso no processo de montagem do esquipamento
- Cada linha de produção é especializada em montar um produto
- Cada linha de porudção deve fabricar 48 produtos 
- O estoque local de cada linha deve ser mantido atualizado no dashboard
- Fica a critério do dashboard estimar o uso de peças e solicitar reabastecimento
- Se faltar pessa, toda a linha de produção para e um timer é iniciado para relatar o tempo ocioso
- A fábrica trabalha durante 16 horas
- Utilizamos os minutos dividido por 60 para fins de testes, ou seja, 1min = 1seg na aplicação
- mensagens são transmitidas por tuplas no formato (remetente, destinatário, código, peça, quantidade)
'''

from utils import *
import paho.mqtt.client as mqtt
import threading
import multiprocessing
import time
import sys
import json



class LinhaProducao:
  def __init__(self, name):
    self.name = name
    self.client = mqtt.Client(self.name)
    self.client.on_connect = self.on_connect
    self.client.on_message = self.on_message
    self.client.connect("localhost", 1883, 60)

    self.estoque = [10] * num_pecas

    try:
      self.client.loop_start()
    except Exception as e:
        self.client.loop_stop()
        self.client.disconnect()
        print(f"Conexão {self.name} encerrada!")


  def on_connect(self, client, userdata, flags, rc):
    print(f"{self.name} conectado ao broker")
    self.client.subscribe(topic_monitor)


  # Função de callback para quando uma mensagem for recebida
  def on_message(self, client, userdata, msg):
    data_json = msg.payload.decode("utf-8")
    remetente, destinatario, code, part_index, quantidade = json.loads(data_json)

    if (code == ra_code and destinatario == self.name):
      self.estoque[part_index] += quantidade
      print(f'\n>> Recebido reposição: peça {part_index}, quantidade {quantidade}\n')


  # Função de ação para montagem de peça em um produto
  def action_part(self, part_index):
    # atualiza o estoque local
    self.estoque[part_index] -= 1

    # serializa a tupla das informações da mensagem e envia pro monitor
    data = json.dumps((self.name, "monitor", ds_code, part_index, 0))
    self.client.publish(topic_estoque, data)

    # considera um tempo de montagem da peça
    time.sleep(random.random())


  def product_assembly(self, prod_name, produto, quantidade):
    for p in range(quantidade):
      print(f"\n{self.name} Montagem do produto {prod_name}: ({p}/{quantidade})")
      
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


class Fabrica2:
  def __init__(self, name):
    self.name = name
    self.client = mqtt.Client(self.name)
    self.client.on_connect = self.on_connect
    self.client.on_message = self.on_message
    self.client.connect("localhost", 1883, 60)

    self.demanda = []

    try:
      self.client.loop_forever()
    except Exception as e:
        print(e)
        self.client.loop_stop()
        self.client.disconnect()
        print(f"Conexão {self.name} encerrada!")


  def on_connect(self, client, userdata, flags, rc):
    print(f"{self.name} conectado ao broker")
    self.client.subscribe(topic_monitor)

  # Função de callback para quando uma mensagem for recebida
  def on_message(self, client, userdata, msg):
    data_json = msg.payload.decode("utf-8")
    remetente, destinatario, code, demanda = json.loads(data_json)

    if (code == fp_code):
      self.demanda = demanda
      if(demanda != []):
        self.administration()
      print()

      

  def administration(self):
    print(type(self.administration))
  
    lotes = []

    for i in range(len(self.demanda)):
      lotes.append((i, self.demanda[i]))

    lotes.sort(key=lambda x: x[1])
    
    distribuicao = [(0,0)] * 8
  
    for i in range(0, 5):
      if (i > 1):
        if (lotes[i][1] % 2 == 0):
          distribuicao[i] = (lotes[i][0], lotes[i][1] // 2)
          distribuicao[i+3] = (lotes[i][0], lotes[i][1] // 2)
        else:
          distribuicao[i] = (lotes[i][0], (lotes[i][1] // 2) + 1)
          distribuicao[i+3] = (lotes[i][0], lotes[i][1] // 2)
      else:
        distribuicao[i] = lotes[i]

    # cria as linhas de produção
    self.linha6 = LinhaProducao("l6")
    self.linha7 = LinhaProducao("l7")
    self.linha8 = LinhaProducao("l8")
    self.linha9 = LinhaProducao("l9")
    self.linha10 = LinhaProducao("l10")
    self.linha11 = LinhaProducao("l11")
    self.linha12 = LinhaProducao("l12")
    self.linha13 = LinhaProducao("l13")

    linha_prod = [self.linha6, self.linha7, self.linha8, self.linha9, self.linha10, self.linha11, self.linha12, self.linha13]
    threads = []

    for i in range(len(self.demanda)):
      thread = threading.Thread(target=linha_prod[i].product_assembly, args=(prod_name[i], produtos[distribuicao[i][0]], distribuicao[i][1]))
      threads.append(thread)

    # Coloca as linhas de produção para trabalharem simultaneamente
    for thread in threads:
      thread.start()

    # Wait for all threads to finish
    for thread in threads:
      thread.join()

    print("\nProducao concluída!")
    
    return


#
#
# Inicializa objeto da fabrica
fabrica = Fabrica2("fabrica2")

