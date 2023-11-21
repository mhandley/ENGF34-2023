b = (1027).to_bytes(2, byteorder='big')
print("1027 as 2 bytes, big endian:", b)

b = (1027).to_bytes(4, byteorder='big')
print("1027 as 4 bytes, big endian:", b)

b = (1027).to_bytes(4, byteorder='little')
print("1027 as 4 bytes, little endian:", b)

b = (2**65).to_bytes(10, byteorder='big')
print("2**65 as 10 bytes, big endian:", b)

b = (-1027).to_bytes(4, byteorder='big', signed=True)
print("-1027 as 4 bytes, big endian:", b)

b = (-1027).to_bytes(4, byteorder='little', signed=True)
print("-1027 as 4 bytes, little endian:", b)

try:
    b = (65536).to_bytes(2, byteorder='big')
    print(b)
except OverflowError as e:
    print("65536 in 2 bytes:", e)
try:
    b = (32768).to_bytes(2, byteorder='big', signed=True)
    print(b)
except OverflowError as e:
    print("32768 in 2 signed bytes:", e)
