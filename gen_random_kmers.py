import sys
import random

k = int(sys.argv[1])
count = int(sys.argv[2])
alphabet = "ACGT"

for i in range(count):
    print(">" + str(i))
    chars = []
    for j in range(k):
        chars.append(alphabet[random.randint(0,3)])
    print("".join(chars))
