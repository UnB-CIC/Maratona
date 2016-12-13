# -*- coding: utf-8 -*-
#    Arquivo: geninput.py
#   Objetivo: Gerar dados de entrada para o problema.


from random import randint, choice
nomes = ['Treco', 'Passas', 'Coco', 'Banana', 'Amargo', 'Leite', 'Branco',
         'Bambu', 'Wasabi', 'Outro']

# Facilitar os exemplos
for x in range(1, 6):
    with open('input/' + str(x), 'w') as f:
        for _ in range(randint(2, 6)):
            f.write('{}\n'.format(choice(nomes)))

# 1 bombom
with open('input/6', 'w') as f:
    f.write('{}\n'.format(choice(nomes)))

#100 bombons
with open('input/7', 'w') as f:
    for _ in range(100):
        f.write('{}\n'.format(choice(nomes)))

for x in range(8, 21):
    with open('input/' + str(x), 'w') as f:
        for _ in range(randint(2, 99)):
            f.write('{}\n'.format(choice(nomes)))
