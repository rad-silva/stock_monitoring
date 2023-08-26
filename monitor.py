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


class Monitor:
  def __init__(self, name):
    self.name = name
    self.client = mqtt.Client(self.name)
    self.client.on_connect = self.on_connect
    self.client.on_message = self.on_message
    self.client.connect("localhost", 1883, 60)


  def on_connect(self, client, userdata, flags, rc):
    print(f"{self.name} conectado ao broker")
    self.client.subscribe(topic_estoque)


  def on_message(self, client, userdata, msg):
    payload = msg.payload.decode("utf-8")
    code, data = payload.split(':')

    # recebeu uma mensagem de utilização de peça vinda da fábrica (decrement stock)
    if code == str(ds_code):
        part_index = int(data)
        estoque_pecas[part_index] -= 1

        # Caso o estoque de alguma peça na linha de produção esteja baixo, envia
        # uma mensagem solicitando reposição da peça {part_index} para o almoxarifado
        if(estoque_pecas[part_index] < production_threshold and not solicita_almoxarifado[part_index]):
            print(f'> Estoque da peça {part_index} baixo -> pedido de reposição para o almoxarifado\n')
            solicita_almoxarifado[part_index] = 1
            self.client.publish(topic_monitor, f"{sa_code}:{part_index}")
    
    # recebeu uma mensagem de resposta de reposição vinda do almoxarifado
    elif code == str(ra_code):
        part_index, quantidade = data.split(',')
        part_index = int(part_index)
        quantidade = int(quantidade)

        # atualiza os dados de estoque do almoxarifado e da fábrica
        solicita_almoxarifado[part_index] = 0
        estoque_pecas[part_index] += quantidade
        estoque_pecas_almoxarife[part_index] -= quantidade

        # replica a mensagem para a fábrica
        self.client.publish(topic_monitor, f"{ra_code}:{part_index},{quantidade}")

        # Verifica se o nível de estoque dessa peça no almoxarifado está baixa
        if(estoque_pecas_almoxarife[part_index] < almoxarife_threshold and not solicita_fornecedor[part_index]):
            print(f'> Estoque da peça {part_index} baixo -> pedido de reposição para o fornecedor\n')
            self.client.publish(topic_monitor, f"{sf_code}:{part_index},{10}")
            solicita_fornecedor[part_index] = 1

        print(f'Notificação de reposição Almoxarifado -> fábrica: peça {part_index}, quantidade {quantidade}')

    # recebeu uma mensagem de resposta de reposição vinda do fornecedor
    elif code and rf_code:
        part_index, quantidade = data.split(',')
        part_index = int(part_index)
        quantidade = int(quantidade)

        # atualiza os dados de estoque do almoxarifado
        solicita_fornecedor[part_index] = 0
        estoque_pecas_almoxarife[part_index] += quantidade

        # replica a mensagem para o almoxarifado
        self.client.publish(topic_monitor, f"{rf_code}:{part_index},{quantidade}")
        print(f'Notificação de reposição fornecedor -> almoxarifado: peça {part_index}, quantidade {quantidade}')
        
    
  def start(self):
    try:
      self.client.loop_forever()
    except KeyboardInterrupt:
      self.client.loop_stop()
      self.client.disconnect()
      print(f"\nconexão {self.name} encerrada!")


#
# Inicializa objeto do monitor
monitor = Monitor("monitor")
monitor.start()


