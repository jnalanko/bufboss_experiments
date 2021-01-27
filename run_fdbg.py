import subprocess
import time
import sys
import os
import uuid
import random
from multiprocessing import Pool

if sys.version_info < (3, 0):
    sys.stdout.write("Error: Python3 required\n")
    sys.exit(1)

def run_get_output(command):
    # Command can have pipes
    sys.stderr.write(command + "\n")
    return subprocess.run(command, shell=True, stdout=subprocess.PIPE).stdout.decode("utf-8").strip()

def run(command):
    sys.stderr.write(command + "\n")
    return subprocess.run(command, shell=True)

def drop_path_and_extension(S):
    return os.path.splitext(os.path.split(S)[1])[0]

def drop_extension(S):
    return os.path.splitext(S)[0]

def concatenate_to(filelist, destination):
    for i, file in enumerate(filelist):
        if i == 0:
            run("cat " + file + " > " + destination)
        else:
            run("cat " + file + " >> " + destination)

# Runs the command and writes to outfile (an opened file object) a line:
# name: time rss
# where time is in seconds and rss is in bytes
def run_timed_rss(command, name, outfile):
    sys.stderr.write(command + "\n")

    # /usr/bin/time -v prints to stderr
    stderr_data = subprocess.run("/usr/bin/time -v " + command, shell=True, stderr=subprocess.PIPE).stderr.decode("utf-8").strip()
    print(stderr_data)
    rss, time = None, None
    for line in stderr_data.split('\n'):
        if "Maximum resident set size (kbytes)" in line:
            rss = int(line.split()[-1]) * 2**10 # bytes
        if "Elapsed (wall clock) time (h:mm:ss or m:ss)" in line:
            token = line.split()[-1]
            hours, minutes, seconds = 0,0,0
            if token.count(":") == 1:
                minutes = float(token.split(":")[0])
                seconds = float(token.split(":")[1])
            elif token.count(":") == 2:
                hours = float(token.split(":")[0])
                minutes = float(token.split(":")[1])
                seconds = float(token.split(":")[2])
            else:
                print("Error parsing /usr/time/time -v")
                assert(False)
            time = hours * 60*60 + minutes*60 + seconds
    if rss == None or time == None:
        print("Error parsing /usr/time/time -v")
        assert(False)
    outfile.write(name + " " + str(time) + " " + str(rss) + "\n")
    outfile.flush()

tempdir = "temp"
run("mkdir -p " + tempdir)

datadir = "data"
outdir = "fdbg_out"
buildlist = datadir + "/coli12_build.txt"
addlist = datadir + "/coli12_add.txt"
dellist = datadir + "/coli12_del.txt"
nodemer_k = 30
edgemer_k = nodemer_k + 1

build_genomes = run_get_output("cat " + buildlist).split('\n')
add_genomes = run_get_output("cat " + addlist).split('\n')
del_genomes = run_get_output("cat " + dellist).split('\n')
resultfile = open("fdbg_results.txt",'w')

# Run fdbg

build_concat = tempdir + "/built.fasta"
concatenate_to(build_genomes, build_concat)
add_concat = tempdir + "/add.fasta"
concatenate_to(add_genomes, add_concat)
del_concat = tempdir + "/del.fasta"
concatenate_to(del_genomes, del_concat)

built = outdir + "/built.dbg"
added = outdir + "/added.dbg"
deleted = outdir + "/deleted.dbg"

run_timed_rss("./bahar-fdbg/cpp-src/fdbg-build-jarno " + build_concat + " " + str(nodemer_k) + " " + built, "fdbg-build", resultfile)

run_timed_rss("./bahar-fdbg/cpp-src/fdbg-add-jarno " + add_concat + " " + str(nodemer_k) + " " + built + " " + added, "fdbg-add", resultfile)

run_timed_rss("./bahar-fdbg/cpp-src/fdbg-del-jarno " + add_concat + " " + str(nodemer_k) + " " + added + " " + deleted, "fdbg-del", resultfile)

