set -u
set -e
set -x

#python3 setup.py 8 1 1
python3 run_bifrost.py
python3 run_bufboss.py
python3 run_fdbg.py
python3 run_dynboss.py
