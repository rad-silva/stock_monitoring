'''
Essa aplicação utiliza a ferramenta Mosquitto https://mosquitto.org/download/ 
como broker do protocolo de mensagens MQTT
- pip install paho-mqtt

Lembre-se de ativar o Mosquitto antes de executar a aplicação
- net start mosquitto
- net stop mosquito
'''


from utils import *
import paho.mqtt.client as mqtt
import time
import json


class Monitor:
  def __init__(self, name):
    self.name = name
    self.client = mqtt.Client(self.name)
    self.client.on_connect = self.on_connect
    self.client.on_message = self.on_message
    self.client.connect("localhost", 1883, 60)

    # armazena o estoque local de cada linha de produção da fábrica 1
    self.frabrica1 = {
      'l1' : estoque_pecas,
      'l2' : estoque_pecas,
      'l3' : estoque_pecas,
      'l4' : estoque_pecas,
      'l5' : estoque_pecas,
  
      'l6' : estoque_pecas,
      'l7' : estoque_pecas,
      'l8' : estoque_pecas,
      'l9' : estoque_pecas,
      'l10' : estoque_pecas,
      'l11' : estoque_pecas,
      'l12' : estoque_pecas,
      'l13' : estoque_pecas,
    }

    self.estoque_data = []
    self.max_estoque = [20] * num_pecas
    self.label = [''] * num_pecas


  def send_msg(self, remetente, destinatario, code, part_index, quantidade):
    data = json.dumps((remetente, destinatario, code, part_index, quantidade))
    self.client.publish(topic_monitor, data)


  def on_connect(self, client, userdata, flags, rc):
    print(f"{self.name} conectado ao broker")
    self.client.subscribe(topic_estoque)


  def on_message(self, client, userdata, msg):
    data_json = msg.payload.decode("utf-8")
    remetente, destinatario, code, part_index, quantidade = json.loads(data_json)

    # recebeu uma mensagem de utilização de peça vinda da fábrica (decrement stock)
    if code == ds_code:
      self.frabrica1[remetente][part_index] -= 1

      # Caso o estoque de alguma peça na linha de produção esteja baixo, envia
      # uma mensagem solicitando reposição da peça {part_index} para o almoxarifado
      if (self.frabrica1[remetente][part_index] < production_threshold and not solicita_almoxarifado[remetente][part_index]):
        # marca uma solicitação da peça 'part_index' pela linha 'remetente'
        solicita_almoxarifado[remetente][part_index] = 1

        #  envia pro almoxarifado
        self.send_msg(remetente, "almoxarifado", sa_code, part_index, quantidade)

        print(f'> Estoque da peça {part_index} baixo na linha {remetente} -> pedido de reposição para o almoxarifado\n')

    
    # recebeu uma mensagem de resposta de reposição vinda do almoxarifado
    elif code == ra_code:
      # atualiza os dados de estoque do almoxarifado e da fábrica
      solicita_almoxarifado[destinatario][part_index] = 0
      estoque_almoxarifado[part_index] -= quantidade
      estoque_fabrica[destinatario][part_index] += quantidade

      # replica a mensagem para a fábrica
      self.send_msg(remetente, destinatario, code, part_index, quantidade)

      # Verifica se o nível de estoque dessa peça no almoxarifado está baixa
      if(estoque_almoxarifado[part_index] < almoxarife_threshold and not solicita_fornecedor[part_index]):
        self.send_msg(self.name, "fornecedor", sf_code, part_index, 10)
        solicita_fornecedor[part_index] = 1
        self.estoque_data[2][part_index] = 'red'

        print(f'> Estoque da peça {part_index} baixo -> pedido de reposição para o fornecedor\n')
      print(f'Notificação de reposição Almoxarifado -> fábrica: peça {part_index}, quantidade {quantidade}')

    # recebeu uma mensagem de resposta de reposição vinda do fornecedor
    elif code == rf_code:
      # atualiza os dados de estoque do almoxarifado
      solicita_fornecedor[part_index] = 0
      print(solicita_fornecedor)
      estoque_almoxarifado[part_index] += quantidade

      if(estoque_almoxarifado[part_index] > almoxarife_threshold):
        self.estoque_data[2][part_index] = 'green'

      # replica a mensagem para o almoxarifado
      self.send_msg(remetente, destinatario, code, part_index, quantidade)

      print(f'Notificação de reposição fornecedor -> almoxarifado: peça {part_index}, quantidade {quantidade}')
        
  
  def prod_puxada(self):
    produtos = [random.randint(1, 5) for _ in range(5)]
    self.send_msg(self.name, "fabrica2", fp_code, produtos, 0)

  def dash(self):
    while(True):
      time.sleep(1)

      for i in range(num_pecas):
        if(estoque_almoxarifado[i] > almoxarife_threshold):
          self.label[i] = 'green'
        else:
          self.label[i] = 'red'

      self.estoque_data.append(self.max_estoque)
      self.estoque_data.append(estoque_almoxarifado)
      self.estoque_data.append(self.label)

      data = json.dumps(self.estoque_data)
      self.client.publish(topic_dashboard, data)

  def start(self):
    try:
      self.prod_puxada()
      self.client.loop_start()
      self.dash()
      
    except KeyboardInterrupt:
      self.client.loop_stop()
      self.client.disconnect()
      print(f"\nconexão {self.name} encerrada!")


#
# Inicializa objeto do monitor
monitor = Monitor("monitor")
monitor.start()


