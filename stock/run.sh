do#!/bin/bash
docker-compose up

docker run -d --name mosquitto --network=host -p 1883:1883 eclipse-mosquitto



docker run -d --name monitor --network=host stock-monitor
docker run -d --name fornecedor --network=host stock-fornecedor
docker run -d --name almoxarifado --network=host stock-almoxarifado
docker run -d --name fabrica_1 --network=host stock-fabrica_1
docker run -d --name fabrica_2 --network=host stock-fabrica_2
