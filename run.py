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

run("mkdir -p temp")
run("mkdir -p bufboss_out")
bufboss_binary = "bufboss/bin/merge"

# First genome is the initial index. Rest are additions
genomes = run_get_output("cat data/coli10.txt").split('\n')

# Concatenate all except the first genomes
print("Concatenating genomes")
run("cat " + genomes[1] + " > temp/genomes.fna")
for i in range(2,len(genomes)):
    run("cat " + genomes[i] + " >> temp/genomes.fna")

print("Running bufboss")
# Build the initial BOSS
run(bufboss_binary + " -d " + genomes[0] + " -o bufboss_out -r -l -k 30")

# Add the rest as a dynamic buffer
run(bufboss_binary + " -i bufboss_out -d temp/genomes.fna -o bufboss_out -r -l -k 30")

