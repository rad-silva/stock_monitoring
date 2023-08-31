# stock_monitoring

Um sistema de monitoramento e controle de estoque de peças em linhas de produção

Objetivo: Garantir que não ocorra ruptura na fabricação por falta de partes.

A empresa tem 2 fábricas com linhas de produção fabricando 5 versões de um produto. Cada versão usa 43 partes do kit base e até 33 partes variáveis. Um sistema será criado para monitorar estoques e pedidos, com cores indicando níveis. Fábrica 1 produz lotes de 48 por linha diariamente; fábrica 2 varia conforme pedidos. A solução usa Docker e MQTT para comunicação entre entidades.sss


# Colaboradores

 Brainer Sueverti de Campos: [hiperbrainer](https://github.com/hiperbrainer) 
 
 Kaique Mancuzo: [KaiqueMancuzo](https://github.com/KaiqueMancuzo)
 
 Pedro Lemos: [PedroLemosM](https://github.com/PedroLemosM)
 
 Ricardo Araújo: [rad-silva](https://github.com/rad-silva)

# Sobre o projeto

## Almoxarifado.py

- Um armazém com estoque para reposição de peças nas fábricas 
- Consideraremos que está localizado a 600 metros da fábrica
- Fica a critério do monitor estimar o uso de peças e solicitar reabastecimento na fábrica
- Fica a critério do monitor checar o nível de estoque no almoxarifado e solicitar peças aos fornecedores

## monitor.py

- Um armazém com estoque para reposição de peças nas fábricas 
- Consideraremos que está localizado a 600 metros da fábrica
- Fica a critério do monitor estimar o uso de peças e solicitar reabastecimento na fábrica
- Fica a critério do monitor checar o nível de estoque no almoxarifado e solicitar peças aos fornecedores

## fabrica_1.py

- Fabricação empurrada -> 1 tipo de equipamento é montado apesar das demandas
- 1 linha de produção (uma thread) tem um buffer (estoque) de peças que será decrementado conforme o uso no processo de montagem do equipamento
- Cada linha de produção é especializada em montar um produto
- Cada linha de porudção deve fabricar 48 produtos 
- O estoque local de cada linha deve ser mantido atualizado no dashboard
- Se faltar peça, toda a linha de produção para e um timer é iniciado para relatar o tempo ocioso
- mensagens são transmitidas por tuplas no formato (remetente, destinatário, código, peça, quantidade)

## fabrica_2.py

- Mesma função da fábrica 1, mas com produtção variável
- Fabricação puxada -> recebe diariamente o tamanho do lote que deve ser produzido (de acordo com a demanda do mercado)
- Existem 8 linhas de produção que podem fabricar qualquer um dos 5 tipos de produtos
- É necessário distribuir as tarefas de produção para que nenhuma linha de produção fique ociosa

## fornecedor.py

- Possui estoque de peças ilimitado
- Consideraremos que está localizado a uma faixa aleatória de distância em metros do almoxarifado
- Fica a critério do monitor checar o nível de estoque no almoxarifado e solicitar peças aos fornecedores
- Pode entregar uma ou mais peças de uma vez

# Como roda?

Basta ter o docker em seu computador e rodar o comando ./run.sh .