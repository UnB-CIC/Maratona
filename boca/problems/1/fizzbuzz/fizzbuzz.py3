#include <stdio.h>

n = int(input())

if 0 == (n % 3):
	print('fizz', sep='')
if 0 == (n % 5):
	print('buzz', sep='')
if (0 != (n % 3)) and (0 != (n % 5)):
	print(n, sep='')
print()
