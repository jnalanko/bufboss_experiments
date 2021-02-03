import matplotlib.pyplot as plt
import sys
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
        elif "add-" in tokens[0]:
            add.append(to_dict3("DynBOSS",  float(tokens[1]), float(tokens[2])))
        elif "del-" in tokens[0]:
            delete.append(to_dict3("DynBOSS",  float(tokens[1]), float(tokens[2])))
        else: # query
            if tokens[0] not in query: query[tokens[0]] = []
            query[tokens[0]].append(("DynBOSS",  float(tokens[1])))

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

# Print the data table for query
for Q in query:
    print(Q)
    for tool, time in query[Q]:
        edgemers = query_metadata[Q]
        time_per_edgemer = time / edgemers # seconds
        print(tool + " " + str(time_per_edgemer * 1e6) + " microseconds/edgemer")

# Plot construction
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



