import sys

n = int(sys.argv[1])

for i in range(0, n + 1):
    print("%.20f" % (128 * (float(i) / 128)))

print("\n\n")
for i in range(0, n + 1):
  a = int(128 * (float(i) / 128))
  if i != a:
    print(i, " != ", a)
