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
