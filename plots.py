import matplotlib.pyplot as plt
import sys

# time (s), working mem (bytes), final disk (bytes)

bifrost_built = {"time": 51.72, "mem": 150736896, "index_disk": 49311755, "name": "Bifrost"}
bifrost_added = {"time": 43.0, "mem": 369369088, "index_disk": 73489117, "name": "Bifrost"}

fdbg_built = {"time": 90.65, "mem": 2798444544, "index_disk": 32489872, "name": "FDBG"}
fdbg_added = {"time": 449.58, "mem": 3805618176, "index_disk": 33107152,  "name": "FDBG"}
fdbg_deleted = {"time": 0, "mem": 0, "index_disk": 0, "name": "FDBG"}

bufboss_built = {"time": 0.64+12.87, "mem": max(528969728,1673670656), "index_disk": 27932 * 2**10, "name": "BufBOSS"}

bufboss_added_runs = []
#bufboss_added_runs.append({"time": 140.1, "mem": 711532544, "index_disk": 0, "name": "BufBOSS-1.0"})
bufboss_added_runs.append({"time": 138.23, "mem": 711827456, "index_disk": 0, "name": "BufBOSS-0.5"})
#bufboss_added_runs.append({"time": 168.49, "mem": 681062400, "index_disk": 0, "name": "BufBOSS-0.25"})
bufboss_added_runs.append({"time": 203.77, "mem": 357457920, "index_disk": 0, "name": "BufBOSS-0.1"})
bufboss_added_runs.append({"time": 262.94, "mem": 293093376, "index_disk": 35708 * 2**10, "name": "BufBOSS-0.05"})
bufboss_added_runs.append({"time": 373.12, "mem": 274550784, "index_disk": 0, "name": "BufBOSS-0.025"})
bufboss_added_runs.append({"time": 616.47, "mem": 256974848, "index_disk": 0, "name": "BufBOSS-0.01"})

bufboss_deleted = {"time": 510.09, "mem": 576802816, "index_disk": 26028 * 2**10, "name": "BufBOSS"}
# Why bufboss_deleted ram is so high? Because: "5257062 dummy edgemers added".

dynboss_built = {"time": 34.49 + 3.35 + 9.35, "mem": max(1642811392, 260165632, 26664960), "index_disk": 0, "name": "DynBOSS"}
dynboss_added = {"time": 6755.0, "mem": 1568399360, "index_disk": 0, "name": "DynBOSS"}
dynboss_deleted = {"time": 10655.0, "mem": 1451417600, "index_disk": 0, "name": "DynBOSS"}

all_built = [bifrost_built, fdbg_built, bufboss_built, dynboss_built] 
all_added = [bifrost_added, dynboss_added, fdbg_added] + bufboss_added_runs 
all_deleted = [bufboss_deleted, dynboss_deleted] 

# Plot construction
fig, ax = plt.subplots()
for D in all_built:
    color = "blue"
    if "BufBOSS" in D["name"]: color = "orange"
    ax.scatter(D["time"], D["mem"], color = color)
    ax.annotate(D["name"], 
                xy=(D["time"], D["mem"]), xycoords='data', # Data point
                xytext=(5, 5), textcoords='offset points') # Text offset
ax.set_xlabel("time (s)")
ax.set_ylabel("mem (bytes)")
ax.set_title("Construction")
plt.show(block = False)

# Plot addition
fig2, ax2 = plt.subplots()
for D in all_added:
    color = "blue"
    if "BufBOSS" in D["name"]: color = "orange"
    ax2.scatter(D["time"], D["mem"], color = color)
    ax2.annotate(D["name"], 
                xy=(D["time"], D["mem"]), xycoords='data', # Data point
                xytext=(5, 5), textcoords='offset points') # Text offset
ax2.set_xlabel("time (s)")
ax2.set_ylabel("mem (bytes)")
ax2.set_title("Addition")
plt.show(block = False)

# Plot deletion
fig3, ax3 = plt.subplots()
ax3.scatter([D["time"] for D in all_deleted], [D["mem"] for D in all_deleted])
for D in all_deleted:
    color = "blue"
    if "BufBOSS" in D["name"]: color = "orange"
    ax3.scatter(D["time"], D["mem"], color = color)
    ax3.annotate(D["name"], 
                xy=(D["time"], D["mem"]), xycoords='data', # Data point
                xytext=(5, 5), textcoords='offset points') # Text offset
ax3.set_xlabel("time (s)")
ax3.set_ylabel("mem (bytes)")
ax3.set_title("Deletion")
plt.show()