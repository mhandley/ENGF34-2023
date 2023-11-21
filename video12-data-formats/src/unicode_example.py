with open('musk.txt', 'rb') as infile:
    line = infile.read()

print(line)
print(line.decode())

with open('musk.txt', 'rt', encoding="utf-8") as infile:
    line = infile.read()
print(line)

