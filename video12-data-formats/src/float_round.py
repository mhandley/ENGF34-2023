import sys

n = int(sys.argv[1])

for i in range(0, n + 1):
    print("%.20f" % (100 * (float(i) / 100)))

print("\n\n")
for i in range(0, n + 1):
  a = int(100 * (float(i) / 100))
  if i != a:
    print(i, " != ", a)
