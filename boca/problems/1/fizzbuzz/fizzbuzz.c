#include <stdio.h>

int main() {
	int n;

	scanf("%d", &n);
	if(!(n%3)) printf("fizz");
	if(!(n%5)) printf("buzz");
	if((n%3) && (n%5)) printf("%d", n);
	printf("\n");

	return 0;
}