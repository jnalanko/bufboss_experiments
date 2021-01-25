import matplotlib.pyplot as plt
import sys

data = []
for line in open(sys.argv[1]):
    if len(line.strip()) == 0: continue
    mem_kb = int(line.split()[2])
    mem_mb = mem_kb / 2**10
    data.append(mem_mb)

plt.plot(data)
plt.show()


