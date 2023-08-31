# Use uma imagem base com Python
FROM python:3.8

# Diretório de trabalho dentro do container
WORKDIR /app

# Copie o código para o diretório de trabalho
COPY . /app

# Instale as dependências
RUN pip install paho-mqtt

# Comando para executar o script
CMD ["python", "fornecedor.py"]