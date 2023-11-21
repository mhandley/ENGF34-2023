
def test_write():
    file = open("store.txt", "wt")
    file.write("Hello\n")
    file.write("World\n")
    file.close()

    with open("store.txt", "rt") as file2:
        for line in file2:
            print(line)

def test_nums():
    file = open("nums.bin", "wb")
    for i in range(1000000, 1000010):
        file.write(i.to_bytes(4, byteorder="little"))
    file.close()

    with open("nums.bin", "rb") as file2:
        file2.seek(8)
        b = file2.read(4)
        i = int.from_bytes(b, byteorder="little")
        print(i)
        print(file2.tell())
    
test_nums()
