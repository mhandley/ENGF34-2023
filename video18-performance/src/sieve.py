import time
from math import sqrt
start = time.time()

n = 100000
prime = [True for i in range(0, n + 1)] 
prime[0]= False
prime[1]= False

p = 2
sqrt_n = sqrt(n)
while p <= sqrt_n: 
    if prime[p]: 
        for i in range(p * 2, n + 1, p): 
            prime[i] = False
    p += 1
    # count the primes

count = 0
for p in range(n + 1): 
    if prime[p]: 
        count += 1

print("Found ", count, "primes in", time.time() - start, "seconds")
