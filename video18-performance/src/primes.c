#include<stdio.h>
#include<stdbool.h>

#define MAXPRIME 100000

int countprimes() {
	int primes[MAXPRIME];
	int primecount = 0;
	for (int test = 2; test < 100000; test++) {
		// check if test is divisible by any smaller prime
		int is_prime = true;
		for (int index = 0; index < primecount; index++) {
			if (test % primes[index] == 0) {
				is_prime = false;
				break;
			}
		}
		if (is_prime) {
			primes[primecount++] = test;
		}
	}
	return primecount;
}

int main() {
	printf("found %d primes\n", countprimes());
}
