'''
Almoxarifado:
- Um armazém com estoque para reposição de peças nas fábricas 
- Consideraremos que está localizado a 600 metros da fábrica
- Fica a critério do monitor estimar o uso de peças e solicitar reabastecimento na fábrica
- Fica a critério do monitor checar o nível de estoque no almoxarifado e solicitar peças aos fornecedores
'''


from utils import *
import paho.mqtt.client as mqtt
import time


class Almoxarifado:
  def __init__(self, name):
    self.name = name
    self.client = mqtt.Client(self.name)
    self.client.on_connect = self.on_connect
    self.client.on_message = self.on_message
    self.client.connect("localhost", 1883, 60)

    self.lista_reposicao = []


  def on_connect(self, client, userdata, flags, rc):
    print(f"{self.name} conectado ao broker")
    self.client.subscribe(topic_monitor)


  def on_message(self, client, userdata, msg):
    payload = msg.payload.decode("utf-8")
    code, data = payload.split(':')
    
    # recebeu uma mensagem de solicitação de reposição vinda da fábrica/monitor
    if code == str(sa_code):
      part_index = int(data)
      self.lista_reposicao.append(part_index)

      print(f"Recebimento de Solicitação de peça {part_index}\n")

    # recebeu uma mensagem de resposta de reposição vinda do fornecedor/monitor
    if code == str(rf_code):
      part_index, quantidade = data.split(',')
      part_index = int(part_index)
      quantidade = int(quantidade)

      # atualiza o estoque do almoxarifado
      estoque_pecas_almoxarife[part_index] += quantidade

      print(f"Recebimento de reposição de peça {part_index}, quantidade {quantidade}\n")


  def action_reposicao(self):
    while(True):
      # Verifica se há reposição de peças pendente
      if (len(self.lista_reposicao) != 0):
        print("Reposição de estoque almoxarifado -> fábrica:")

        # aguarda caso apareça novas solicitações
        time.sleep(5)

        # atualiza todos as peças solicitadas
        for _, part_index in enumerate(self.lista_reposicao):
          if (estoque_pecas_almoxarife[part_index] > 0):
            quantidade = min(estoque_pecas_almoxarife[part_index], max_stock_fabrica)
            estoque_pecas_almoxarife[part_index] -= quantidade
            self.lista_reposicao.remove(part_index)

            # envia resposta de reposição
            self.client.publish(topic_estoque, f"{ra_code}:{part_index},{quantidade}") 
            print(f" - envio de peça {part_index}, quantidade {quantidade}")
          
          else:
            print(f" - falta de peça {part_index}")

        print()

    
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
almoxarifado = Almoxarifado("Almoxarifado")
almoxarifado.start()
