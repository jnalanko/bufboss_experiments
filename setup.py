
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

def parse_our_printed_time(filename):
    for line in open(filename).readlines():
        if ("Time for all queries:" in line) or ("Time for additions:" in line):
            return float(line.split()[-2])
    print("Error parsing time from " + filename)
    assert(False)

def run_get_output(command):
    # Command can have pipes
    sys.stderr.write(command + "\n")
    proc = subprocess.run(command, shell=True, stdout=subprocess.PIPE)
    if proc.returncode != 0:
        print("Error: nonzero return code for command: " + command)
        sys.exit(1)
    return proc.stdout.decode("utf-8").strip()

def run(command):
    sys.stderr.write(command + "\n")
    if subprocess.run(command, shell=True).returncode != 0:
        print("Error: nonzero return code for command: " + command)
        sys.exit(1)

def run_to_files(command, out_prefix):
    sys.stderr.write(command + "\n")
    stdout_file = out_prefix + ".stdout.txt"
    stderr_file = out_prefix + ".stderr.txt"
    sys.stderr.write("stdout to " + stdout_file + "\n")
    sys.stderr.write("stderr to " + stderr_file + "\n")
    stdout_stream = open(stdout_file, 'w')
    stderr_stream = open(stderr_file, 'w')
    if subprocess.run(command, shell=True, stdout=stdout_stream, stderr=stderr_stream).returncode != 0:
        print("Error: nonzero return code for command: " + command)
        sys.exit(1)

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

# Returns pair (time seconds, RSS bytes)
def parse_usr_bin_time(stderr_file):
    rss, time = None, None
    for line in open(stderr_file):
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
        print("Error parsing /usr/time/time -v from " + stderr_file)
        assert(False)

    return time, rss

# Path can be a directory or a single file
# If directory, returns the total size of the directory
# If file, returns the file size
def get_disk_size_bytes(path):
    return int(run_get_output("du -d 0 -b "  + path).split()[0])

experiment_dir = None
#datadir = experiment_dir + "/data"
#tempdir = experiment_dir + "/temp"

nodemer_k = 30
edgemer_k = nodemer_k + 1


def fasta_count_edgemers(fastafile):
    seq_len = 0
    total_edgemers = 0
    for line in open(fastafile):
        line = line.strip()
        if len(line) == 0: continue
        if line[0] == '>':
            total_edgemers += max(0, seq_len - edgemer_k + 1)
            seq_len = 0
        else:
            seq_len += len(line)
    total_edgemers += max(0, seq_len - edgemer_k + 1) # Last sequence
    return total_edgemers

class ExperimentConfig:

    def __init__(self, buildfile = None, buildfile_rc = None, addfile = None, addfile_rc = None, delfile = None, delfile_rc = None, queryfiles = None, experiment_dir = None, tempdir = None):
        if buildfile != None: assert experiment_dir != None # If first argument is given, require that all arguments are given
        self.buildfile = buildfile
        self.buildfile_rc = buildfile_rc
        self.addfile = addfile
        self.addfile_rc = addfile_rc
        self.delfile = delfile
        self.delfile_rc = delfile_rc
        self.query_inputs = queryfiles
        self.experiment_dir = experiment_dir
        self.temp_dir = tempdir
    
    def serialize(self, filename):
        f = open(filename, 'w')

        f.write(self.experiment_dir + "\n")
        f.write(self.temp_dir + "\n")

        f.write(self.buildfile + "\n")
        f.write(self.buildfile_rc + "\n")

        f.write(self.addfile + "\n")
        f.write(self.addfile_rc + "\n")

        f.write(self.delfile + "\n")
        f.write(self.delfile_rc + "\n")

        for query_name in self.query_inputs:
            f.write(query_name + " " + self.query_inputs[query_name] + "\n")

    def load(self, filename):
        lines = open(filename, 'r').readlines()
        self.experiment_dir = lines[0].strip()
        self.temp_dir = lines[1].strip()

        self.buildfile = lines[2].strip()
        self.buildfile_rc = lines[3].strip()

        self.addfile = lines[4].strip()
        self.addfile_rc = lines[5].strip()

        self.delfile = lines[6].strip()
        self.delfile_rc = lines[7].strip()

        self.query_inputs = dict()
        for line in lines[8:]:
            name, path = line.split()[0].strip(), line.split()[1].strip()
            self.query_inputs[name] = path
            






def write_config(buildfile, buildfile_rc, addfile, addfile_rc, delfile, delfile_rc, queryfiles, experiment_dir):
    open(experiment_dir + "/buildfiles.txt", 'w').write("build " + buildfile + "\n" + "build_rc " + buildfile_rc + "\n")
    open(experiment_dir + "/addfiles.txt", 'w').write("add " + addfile + "\n" + "add_rc " + addfile_rc + "\n")
    open(experiment_dir + "/delfiles.txt", 'w').write("del " + delfile + "\n" + "del_rc " + delfile_rc + "\n")

    querylist = open(experiment_dir + "/queryfiles.txt", 'w')
    for query_name in queryfiles:
        querylist.write(query_name + " " + queryfiles[query_name] + "\n")


def generate_input_files_from_readfile(readfile, experiment_dir, build_percentage, add_percentage, del_percentage):

    datadir = experiment_dir + "/data"
    tempdir = experiment_dir + "/temp"

    run("mkdir -p " + str(datadir))
    run("mkdir -p " + str(tempdir))
    run("mkdir -p " + str(experiment_dir))
    run("mkdir -p " + str(experiment_dir + "/lists"))

    query_inputs = {"query-random_edgemers": experiment_dir + "/data/random/edgemers.fasta",
                    "query-random_sequence": experiment_dir + "/data/random/sequence.fasta",
                    "query-existing_build_edgemers": experiment_dir + "/data/existing/build_edgemers.fasta",
                    "query-existing_build_sequence": experiment_dir + "/data/existing/build_sequence.fasta",
                    "query-existing_added_edgemers": experiment_dir + "/data/existing/added_edgemers.fasta",
                    "query-existing_added_sequence" : experiment_dir + "/data/existing/added_sequence.fasta"}

    query_metadatafile = experiment_dir + "/lists/query_metadata.txt"

    build_concat = experiment_dir + "/data/build.fasta"
    add_concat = experiment_dir + "/data/add.fasta"
    del_concat = experiment_dir + "/data/del.fasta"

    build_concat_with_rc = experiment_dir + "/data/build_with_rc.fasta"
    add_concat_with_rc = experiment_dir + "/data/add_with_rc.fasta"
    del_concat_with_rc = experiment_dir + "/data/del_with_rc.fasta"

    config = ExperimentConfig (build_concat, build_concat_with_rc, add_concat, add_concat_with_rc, del_concat, del_concat_with_rc, query_inputs, experiment_dir, tempdir)
    config.serialize(experiment_dir + "/config.txt")

    # Split to build, add, del
    run("./input_cleaning/split_and_remove_non_ACGT " + str(edgemer_k) + " " + readfile + " " + str(build_percentage) + " " + str(add_percentage) + " " + str(del_percentage) + " " + build_concat + " " + add_concat + " " + del_concat)

    # For tools that don't index reverse complements (looking at you dynboss), create input files with
    # concatenated reverse complements in the end
    run("./input_cleaning/get_rc " + build_concat + " temp/temp_rc.fasta")
    run("cat " + build_concat + " temp/temp_rc.fasta > " + build_concat_with_rc) 

    run("./input_cleaning/get_rc " + add_concat + " temp/temp_rc.fasta")
    run("cat " + add_concat + " temp/temp_rc.fasta > " + add_concat_with_rc)

    run("./input_cleaning/get_rc " + del_concat + " temp/temp_rc.fasta")
    run("cat " + del_concat + " temp/temp_rc.fasta > " + del_concat_with_rc)

    # Generate random queries
    run("mkdir -p " + experiment_dir + "/data/random")
    run("python3 gen_random_kmers.py 31 1000000 > " + query_inputs["query-random_edgemers"]) # Million edgemers
    run("python3 gen_random_kmers.py 1000000 1 > " + query_inputs["query-random_sequence"]) # Million - k + 1 edgemers

    # Generate existing queries...
    run("mkdir -p " + experiment_dir + "/data/existing")

    # ...for existing k-mers, build a bufboss and sample from there. First for build kmers...
    index_dir = tempdir + "/buffboss"
    run("mkdir -p " + index_dir)
    run("./bufboss/KMC/bin/kmc -k31 -m1 -ci1 -cs1 -fm " + build_concat + " " + tempdir + "/kmc_db temp")
    run("./bufboss/bin/bufboss_build --KMC " + tempdir + "/kmc_db -o " + index_dir + " -t " + tempdir)
    run("./bufboss/bin/bufboss_sample_random_edgemers -i " + index_dir + " -o " + query_inputs["query-existing_build_edgemers"] + " --count 1000000")

    # ...then for added kmers (reuse the same index dir)
    run("./bufboss/KMC/bin/kmc -k31 -m1 -ci1 -cs1 -fm " + add_concat + " " + tempdir + "/kmc_db temp")
    run("./bufboss/bin/bufboss_build --KMC " + tempdir + "/kmc_db -o " + index_dir + " -t " + tempdir)
    run("./bufboss/bin/bufboss_sample_random_edgemers -i " + index_dir + " -o " + query_inputs["query-existing_added_edgemers"] + " --count 1000000")

    # For existing sequences, take 1 million base pairs from buildlist and addlist
    run("./input_cleaning/take_prefix 1000000 " + build_concat + " " + query_inputs["query-existing_build_sequence"])
    run("./input_cleaning/take_prefix 1000000 " + add_concat + " " + query_inputs["query-existing_added_sequence"])

    print("Calculating metadata")
    metadata = open(query_metadatafile,'w')
    for name in query_inputs:
        metadata.write(name + " " + str(fasta_count_edgemers(query_inputs[name])) + "\n")

# Takes number of genomes to build, add and del respectively.
if __name__ == "__main__":
    if sys.argv[1] == "reads-split":
        readfile = sys.argv[2]
        experiment_dir = sys.argv[3]
        build_percentage = int(sys.argv[4])
        add_percentage = int(sys.argv[5])
        del_percentage = int(sys.argv[6])
        assert(build_percentage + add_percentage + del_percentage == 100)
        generate_input_files_from_readfile(readfile, experiment_dir, build_percentage, add_percentage, del_percentage)
    else:
        print("Invalid experiment class: " + sys.argv[1])
        quit(1)
