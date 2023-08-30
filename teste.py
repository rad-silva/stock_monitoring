import random

demanda = [random.randint(1,9) for i in range(5)]
lotes = []

for i in range(len(demanda)):
  lotes.append((i, demanda[i]))

lotes.sort(key=lambda x: x[1])

print(demanda)
print(lotes)

distribuicao = [(0,0)] * 8

for i in range(0, 5):
  if (i > 1):
    if (lotes[i][1] % 2 == 0):
      distribuicao[i] = (lotes[i][0], lotes[i][1] // 2)
      distribuicao[i+3] = (lotes[i][0], lotes[i][1] // 2)
    else:
      distribuicao[i] = (lotes[i][0], (lotes[i][1] // 2) + 1)
      distribuicao[i+3] = (lotes[i][0], lotes[i][1] // 2)
  else:
    distribuicao[i] = lotes[i]

print(distribuicao)