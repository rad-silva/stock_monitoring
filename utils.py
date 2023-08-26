import random

# código para identificar operação destinatário no início do payload 
ds_code = b'00001' # decrease stock
sa_code = b'00010' # solicitação de reposição almoxarife
sf_code = b'00100' # solicitação de reposição fornecedor 
ra_code = b'01000' # resposta de de reposição almoxarife
rf_code = b'10000' # resposta de de reposição forncedor

# Tópicos para receber e enviar dados ao monitor
topic_monitor = 'topic/monitor'
topic_estoque = 'topic/estoque'

max_stock_fabrica = 10

# número de peças diferentes que a fábrica utiliza
num_pecas = 10

# estoque de peças de uma linha de produção
estoque_pecas = [10] * num_pecas

# estoque de peças do almoxarifado
estoque_pecas_almoxarife = [20] * num_pecas

# gera uma lista de peças utilizadas na montagem de um produto
# por simplicidade, vamos considerar que cada peça deve ser utilizada na ordem de seu índice
produto = [random.randint(1, 6) if random.choice([True, False]) else 0 for _ in range(num_pecas)]

# gera uma lista de tempo utilizado na montagem de cada peça do produto
timer = [random.randint(1, 5)/10 for _ in range(num_pecas)]

# define um limiar para a quantidade de peças viável 
almoxarife_threshold = 8
production_threshold = 5

# estoque de peças do almoxarifado
solicita_almoxarifado = [0] * num_pecas

# estoque de peças do almoxarifado
solicita_fornecedor= [0] * num_pecas