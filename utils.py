import random

# Tópicos para receber e enviar dados ao monitor
topic_monitor = 'topic/monitor'
topic_estoque = 'topic/estoque'

# número de peças diferentes que a fábrica utiliza
num_pecas = 10

# estoque de peças de uma linha de produção
estoque_pecas = [10] * num_pecas

# gera uma lista de peças utilizadas na montagem de um produto
# por simplicidade, vamos considerar que cada peça deve ser utilizada na ordem de seu índice
produto = [random.randint(1, 6) if random.choice([True, False]) else 0 for _ in range(num_pecas)]

# gera uma lista de tempo utilizado na montagem de cada peça do produto
timer = [random.randint(1, 5)/10 for _ in range(num_pecas)]

