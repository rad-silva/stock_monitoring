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