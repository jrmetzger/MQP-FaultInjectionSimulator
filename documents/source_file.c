#include<stdio.h>
#include<stdbool.h>

int add(int a, int b){
	int sum = a + b;
	return sum;
}
int main(){
	int a = 0;
	int b = 1;
	bool decrease = false;
	while(a < b){
		if(a < 0) decrease = false;
		if(a > 100) decrease = true;
		if (decrease)
		{	a = a - 1;
			b = b - 1;
		}else
		{	a = a + 1;
			b = b + 1;}

		int sum = add(a,b);
		if (sum%2 != 1) return 0;

		printf("Feedback Line\n");
		printf("Num Values: A= %d\tB= %d\n",a,b);
	}
	printf("Loop Finished\n");
}