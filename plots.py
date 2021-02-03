import matplotlib.pyplot as plt
import sys
import numpy as np
from setup import *

def parse_summaries():

    build = [] # Data points are triples (name, time, rss) represented as dicts
    add = [] # Data points are triples (name, time, rss) represented as dicts
    delete = [] # Data points are triples (name, time, rss) represented as dicts
    query = {} # Here we have dict {query-dataset-name -> list of pairs (tool, time)}

    to_dict3 = lambda name, time, mem : {"name" : name, "time": time, "mem": mem}

    # Parse bifrost
    for line in open("bifrost_results/summary.txt"):
        tokens = line.split()
        if tokens[0] == "build":
            build.append(to_dict3("Bifrost",  float(tokens[1]), float(tokens[2])))
        elif tokens[0] == "add":
            add.append(to_dict3("Bifrost",  float(tokens[1]), float(tokens[2])))
        else: # query
            if tokens[0] not in query: query[tokens[0]] = []
            query[tokens[0]].append(("Bifrost",  float(tokens[1])))

    # Parse bufboss
    for line in open("bufboss_results/summary.txt"):
        tokens = line.split()
        if tokens[0] == "build":
            build.append(to_dict3("BufBOSS",  float(tokens[1]), float(tokens[2])))
        elif "add-" in tokens[0]:
            add.append(to_dict3("BufBOSS-" + tokens[0].split("-")[-1],  float(tokens[1]), float(tokens[2])))
        elif "del-" in tokens[0]:
            delete.append(to_dict3("BufBOSS-" + tokens[0].split("-")[-1],  float(tokens[1]), float(tokens[2])))
        else: # query
            if tokens[0] not in query: query[tokens[0]] = []
            query[tokens[0]].append(("BufBOSS",  float(tokens[1])))

    # Parse dynboss
    for line in open("dynboss_results/summary.txt"):
        tokens = line.split()
        if tokens[0] == "build":
            build.append(to_dict3("DynBOSS",  float(tokens[1]), float(tokens[2])))
        elif tokens[0] == "add":
            add.append(to_dict3("DynBOSS",  float(tokens[1]), float(tokens[2])))
        else: # query
            if tokens[0] not in query: query[tokens[0]] = []
            query[tokens[0]].append(("DynBOSS",  float(tokens[1])))

    # Parse fdbg
    for line in open("fdbg_results/summary.txt"):
        tokens = line.split()
        if tokens[0] == "build":
            build.append(to_dict3("FDBG",  float(tokens[1]), float(tokens[2])))
        elif tokens[0] == "add":
            add.append(to_dict3("FDBG",  float(tokens[1]), float(tokens[2])))
        else: # query
            if tokens[0] not in query: query[tokens[0]] = []
            query[tokens[0]].append(("FDBG",  float(tokens[1])))

    return build, add, delete, query

# Returns dict for numebr of k-mers in each query input
def parse_query_metadata():
    D = dict()
    for line in open("lists/query_metadata.txt"):
        D[line.split()[0]] = int(line.split()[-1])
    return D

build, add, delete, query = parse_summaries()
query_metadata = parse_query_metadata()
print(build)
print(add)
print(query)

#
# Print and plot the data for query
#

query_inputs = []
bufboss_queries = []
bifrost_queries = []
fdbg_queries = []

for Q in query:
    print(Q)
    query_inputs.append(Q)
    for tool, time in query[Q]:
        edgemers = query_metadata[Q]
        time_per_edgemer = time / edgemers # seconds
        print(tool + " " + str(time_per_edgemer) + " seconds/edgemer")
        if tool == "Bifrost": bifrost_queries.append(time_per_edgemer)
        if tool == "BufBOSS": bufboss_queries.append(time_per_edgemer)
        if tool == "FDBG": fdbg_queries.append(time_per_edgemer)

x = np.arange(len(query_inputs))  # the label locations
width = 0.8  # the width of the bars

fig, ax = plt.subplots()
rects1 = ax.bar(x + 0*width/3, bifrost_queries, width/3, label='Bifrost')
rects2 = ax.bar(x + 1*width/3, bufboss_queries, width/3, label='BufBOSS')
rects3 = ax.bar(x + 2*width/3, fdbg_queries, width/3, label='FDBG')

# Add some text for labels, title and custom x-axis tick labels, etc.
ax.set_ylabel('Seconds per edgemer')
ax.set_title('Query time')
ax.set_xticks(x)
ax.set_xticklabels(query_inputs, rotation = 45)
ax.set_yscale("log")
ax.legend()
fig.tight_layout()
plt.show(block = False)

#
# Plot construction
#

fig, ax = plt.subplots()
for D in build:
    color = "blue"
    if "BufBOSS" in D["name"]: color = "orange"
    ax.scatter(D["time"], D["mem"], color = color)
    ax.annotate(D["name"], 
                xy=(D["time"], D["mem"]), xycoords='data', # Data point
                xytext=(5, 5), textcoords='offset points') # Text offset
ax.set_xlim((0, None))
ax.set_ylim((0, None))
ax.set_xlabel("time (s)")
ax.set_ylabel("mem (bytes)")
ax.set_title("Construction")
plt.show(block = False)

# Plot addition
fig2, ax2 = plt.subplots()
for D in add:
    color = "blue"
    if "BufBOSS" in D["name"]: color = "orange"
    ax2.scatter(D["time"], D["mem"], color = color)
    ax2.annotate(D["name"], 
                xy=(D["time"], D["mem"]), xycoords='data', # Data point
                xytext=(5, 5), textcoords='offset points') # Text offset
ax.set_xlim((0, None))
ax.set_ylim((0, None))
ax2.set_xlabel("time (s)")
ax2.set_ylabel("mem (bytes)")
ax2.set_title("Addition")
plt.show(block = True)



