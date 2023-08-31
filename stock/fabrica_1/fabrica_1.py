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
- mensagens são transmitidas por tuplas no formato (remetente, destinatário, código, peça, quantidade)
'''


import paho.mqtt.client as mqtt
import threading
import time
import sys
import json

import random

# código para identificar operação destinatário no início do payload 
ds_code = 1 # decrease stock
sa_code = 2 # solicitação de reposição almoxarife
sf_code = 3 # solicitação de reposição fornecedor 
ra_code = 4 # resposta de de reposição almoxarife
rf_code = 5 # resposta de de reposição forncedor
fp_code = 6 # 

# Tópicos para receber e enviar dados ao monitor
topic_monitor = 'topic/monitor'
topic_estoque = 'topic/estoque'
topic_dashboard = 'topic/dashboard'

max_stock_fabrica = 50

# número de peças diferentes que a fábrica utiliza
num_pecas = 10
num_pecas_base = 7
num_pecas_varia = 3

# estoque de peças de uma linha de produção
estoque_pecas = [10] * num_pecas

estoque_fabrica = {
  'l1' : [max_stock_fabrica] * num_pecas,
  'l2' : [max_stock_fabrica] * num_pecas,
  'l3' : [max_stock_fabrica] * num_pecas,
  'l4' : [max_stock_fabrica] * num_pecas,
  'l5' : [max_stock_fabrica] * num_pecas,
  'l6' : [max_stock_fabrica] * num_pecas,
  'l7' : [max_stock_fabrica] * num_pecas,
  'l8' : [max_stock_fabrica] * num_pecas,
  'l9' : [max_stock_fabrica] * num_pecas,
  'l10' : [max_stock_fabrica] * num_pecas,
  'l11' : [max_stock_fabrica] * num_pecas,
  'l12' : [max_stock_fabrica] * num_pecas,
  'l13' : [max_stock_fabrica] * num_pecas,
}

# estoque de peças do almoxarifado
estoque_almoxarifado = [100] * num_pecas

# gera uma lista de peças utilizadas na montagem de um produto
# por simplicidade, vamos considerar que cada peça deve ser utilizada na ordem de seu índice
produto = [random.randint(1, 6) if random.choice([True, False]) else 0 for _ in range(num_pecas)]

kit_base = [random.randint(1, 6) if random.choice([True, False]) else 0 for _ in range(num_pecas_base)]
pv1 = kit_base + [random.randint(1, 6) if random.choice([True, False]) else 0 for _ in range(num_pecas - num_pecas_base)]
pv2 = kit_base + [random.randint(1, 6) if random.choice([True, False]) else 0 for _ in range(num_pecas - num_pecas_base)]
pv3 = kit_base + [random.randint(1, 6) if random.choice([True, False]) else 0 for _ in range(num_pecas - num_pecas_base)]
pv4 = kit_base + [random.randint(1, 6) if random.choice([True, False]) else 0 for _ in range(num_pecas - num_pecas_base)]
pv5 = kit_base + [random.randint(1, 6) if random.choice([True, False]) else 0 for _ in range(num_pecas - num_pecas_base)]

# gera uma lista de tempo utilizado na montagem de cada peça do produto
timer = [random.randint(1, 5)/10 for _ in range(num_pecas)]

# define um limiar para a quantidade de peças viável 
almoxarife_threshold = 10
almoxarife_baseline = 30
production_threshold = 5

# estoque de peças do almoxarifado
# solicita_almoxarifado = [0] * num_pecas

# estoque de peças do almoxarifado
solicita_fornecedor= [0] * num_pecas

solicita_almoxarifado = {
  'l1' : [0] * num_pecas,
  'l2' : [0] * num_pecas,
  'l3' : [0] * num_pecas,
  'l4' : [0] * num_pecas,
  'l5' : [0] * num_pecas,
  'l6' : [0] * num_pecas,
  'l7' : [0] * num_pecas,
  'l8' : [0] * num_pecas,
  'l9' : [0] * num_pecas,
  'l10' : [0] * num_pecas,
  'l11' : [0] * num_pecas,
  'l12' : [0] * num_pecas,
  'l13' : [0] * num_pecas,
}

prod_name = ['pv1', 'pv2', 'pv3', 'pv4', 'pv5']
produtos = [pv1, pv2, pv3, pv4, pv5]

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


class Fabrica:
  def __init__(self, name):
    self.name = name

  def administration(self):
    total_produtos = 5

    # cria as linhas de produção
    self.linha1 = LinhaProducao("l1")
    self.linha2 = LinhaProducao("l2")
    self.linha3 = LinhaProducao("l3")
    self.linha4 = LinhaProducao("l4")
    self.linha5 = LinhaProducao("l5")

    linha_prod = [self.linha1, self.linha2, self.linha3, self.linha4, self.linha5]
    threads = []

    for i in range(len(linha_prod)):
      thread = threading.Thread(target=linha_prod[i].product_assembly, args=(prod_name[i], produtos[i], total_produtos))
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
fabrica = Fabrica("fabrica1")
fabrica.administration()
