# -*- coding: utf-8 -*-
#    Arquivo: geninput.py3
#   Objetivo: Gerar dados de entrada para o problema.


for x in range(1, 32):
	with open('input/' + str(x), 'w') as f:
		f.write('{}\n'.format(x))
