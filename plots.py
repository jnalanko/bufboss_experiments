import matplotlib.pyplot as plt
import sys

# time (s), working mem (bytes), final disk (bytes)

bifrost_built = {"time": 51.72, "mem": 150736896, "index_disk": 49311755}
bifrost_added = {"time": 43.0, "mem": 369369088, "index_disk": 73489117}

fdbg_built = {"time": 90.65, "mem": 2798444544, "index_disk": 32489872}
fdbg_added = {"time": 449.58, "mem": 3805618176, "index_disk": 33107152}
fdbg_deleted = {"time": 0, "mem": 0, "index_disk": 0}

bufboss_built = {"time": 121.68, "mem": 2456678400, "index_disk": 28004 * 2**10}
bufboss_added = {"time": 510.73, "mem": 234758144, "index_disk": 0}
bufboss_deleted = {"time": 6.08, "mem": 10121216, "index_disk": 0}

dynboss_built = {"time": 34.49 + 3.35 + 9.35, "mem": max(1642811392, 260165632, 26664960), "index_disk": 0}
dynboss_added = {"time": 0, "mem": 0, "index_disk": 0}
dynboss_deleted = {"time": 0, "mem": 0, "index_disk": 0}

all_built = [bifrost_built, fdbg_built, bufboss_built, dynboss_built] 
names = ["Bifrost", "FDBG", "BufBOSS", "DynBOSS"]

# Plot build
fig, ax = plt.subplots()
ax.scatter([D["time"] for D in all_built], [D["mem"] for D in all_built])
for i, name in enumerate(names):
    ax.annotate(name, 
                xy=(all_built[i]["time"], all_built[i]["mem"]), xycoords='data', # Data point
                xytext=(5, 5), textcoords='offset points') # Text offset
#plt.bar(range(4), [bifrost_built[0], fdbg_built[0], bufboss_built[0], dynboss_built[0]])
#plt.xticks(range(4), ("Bifrost", "FDBG", "BufBOSS", "DynBOSS"))
ax.set_xlabel("time (s)")
ax.set_ylabel("mem (bytes)")
ax.set_title("Construction")
plt.show()