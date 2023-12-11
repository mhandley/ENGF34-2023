import time
from ctypes import *
libprimes = CDLL("./libprimes.so")
 
#call C function to check connection
count = libprimes.countprimes() 
 
print("counted ", count, "primes")
