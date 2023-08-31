'''
Almoxarifado:
- Um armazém com estoque para reposição de peças nas fábricas 
- Consideraremos que está localizado a 600 metros da fábrica
- Fica a critério do monitor estimar o uso de peças e solicitar reabastecimento na fábrica
- Fica a critério do monitor checar o nível de estoque no almoxarifado e solicitar peças aos fornecedores
'''


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

max_stock_fabrica = 10

# número de peças diferentes que a fábrica utiliza
num_pecas = 10
num_pecas_base = 7
num_pecas_varia = 3

# estoque de peças de uma linha de produção
estoque_pecas = [10] * num_pecas

estoque_fabrica = {
  'l1' : [10] * num_pecas,
  'l2' : [10] * num_pecas,
  'l3' : [10] * num_pecas,
  'l4' : [10] * num_pecas,
  'l5' : [10] * num_pecas,
  'l6' : [10] * num_pecas,
  'l7' : [10] * num_pecas,
  'l8' : [10] * num_pecas,
  'l9' : [10] * num_pecas,
  'l10' : [10] * num_pecas,
  'l11' : [10] * num_pecas,
  'l12' : [10] * num_pecas,
  'l13' : [10] * num_pecas,
}

# estoque de peças do almoxarifado
estoque_almoxarifado = [30] * num_pecas

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
almoxarife_threshold = 8
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

import paho.mqtt.client as mqtt
import json
import time


class Almoxarifado:
  def __init__(self, name):
    self.name = name
    self.client = mqtt.Client(self.name)
    self.client.on_connect = self.on_connect
    self.client.on_message = self.on_message
    self.client.connect("localhost", 1883, 60)

    self.num_pedidos = 0
    self.lista_reposicao = []

    # para cada peça, cria uma lista vazia que conterá o nome de qual linha de reposição solicitou reposição
    for _ in range(num_pecas):
      self.lista_reposicao.append([])


  def on_connect(self, client, userdata, flags, rc):
    print(f"{self.name} conectado ao broker")
    self.client.subscribe(topic_monitor)


  def on_message(self, client, userdata, msg):
    data_json = msg.payload.decode("utf-8")
    remetente, destinatario, code, part_index, quantidade = json.loads(data_json)

    # recebeu uma mensagem de solicitação de reposição vinda da fábrica/monitor
    if code == sa_code:
      # adiciona na lista de reposição da peça 'part_index' qual 'linha' pediu reposição
      self.lista_reposicao[part_index].append(remetente)
      self.num_pedidos += 1

      print(f"Recebimento de Solicitação de peça {part_index}\n")

    # recebeu uma mensagem de resposta de reposição vinda do fornecedor/monitor
    if code == rf_code:
      estoque_almoxarifado[part_index] += quantidade
      print(f"Recebimento de reposição de peça {part_index}, quantidade {quantidade}\n")


  def action_reposicao(self):
    while(True):
      #print("Reposição de estoque almoxarifado -> fábrica:")
      time.sleep(3)  # aguarda caso apareça novas solicitações

      for part_index, linha in enumerate(self.lista_reposicao):
        if (estoque_almoxarifado[part_index] > 0):
          # para cada linha de produção que solicitou reposição de 'part_index'
          for linha_name in linha:
            if (estoque_almoxarifado[part_index] > 0):
              # decrementa o estoque do almoxarifado
              quantidade = min(estoque_pecas[part_index], max_stock_fabrica)
              estoque_almoxarifado[part_index] -= quantidade

              # remove o pedido da 'linha l'
              self.lista_reposicao[part_index].remove(linha_name)

              data = json.dumps((self.name, linha_name, ra_code, part_index, quantidade))
              self.client.publish(topic_estoque, data)
              print(f" - envio de peça {part_index} para {linha_name}")
        else :
          print(f'falta de peça {part_index}\n')
        
        # else:
        #   print(f" - falta de peça {part_index}")


    
  def start(self):
    try:
      self.client.loop_start() # inicia um loop MQTT em uma thread separada
      self.action_reposicao()   # mantém a execução da próxima parte do programa
    except KeyboardInterrupt:
      self.client.loop_stop()
      self.client.disconnect()
      print(f"\nconexão {self.name} encerrada!")


#
# Inicializa objeto do Almoxarifado
almoxarifado = Almoxarifado("almoxarifado")
almoxarifado.start()
