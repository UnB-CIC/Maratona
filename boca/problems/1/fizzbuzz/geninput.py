# -*- coding: utf-8 -*-
#    Arquivo: genio.py
#   Objetivo: Gerar dados de Entrada/Saída para o problema.


from random import choice, randint

for x in range(1, 11):
    with open('input/{}'.format(x), 'w') as f:
        f.write('{}\n'.format(x))
    with open('input/{}'.format(x + 10), 'w') as f:
        f.write('{}\n'.format(choice([3, 5, 15]) * randint(10, 10000)))
    with open('input/{}'.format(x + 20), 'w') as f:
        f.write('{}\n'.format(randint(100000, (2**32) - 1)))
