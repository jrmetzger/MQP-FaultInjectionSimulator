#include<stdio.h>

int add(int a, int b) {
	int sum = a + b;
	return sum;
}

int main() {
	int a = 5;
	int b = 10;
	while(1 < 2) {
		a = add(a, b); 		// a=15
		b = a - b; 			// b = 5
		a = a - b; 			// a = 10

		if(a%5 != b%5) {
			return 0;
		}
		printf("%d\t%d\n",a,b);
	}
	printf("EXITED");
}


