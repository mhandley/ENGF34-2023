from time import time

primes = []
starttime = time()
primes = [0 for i in range(100000)]
print("initialized in", time() - starttime, "seconds")

primecount = 0

for test in range(2,100000):
    is_prime = True
    # check if test is divisible by any smaller prime
    for index in range(primecount):
        if test % primes[index] == 0:
            is_prime = False
            break
    if is_prime:
        primes[primecount] = test
        primecount += 1
print("Found ", primecount, "primes")

