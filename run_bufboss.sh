set -u
set -e
set -x 

./bufboss/bin/bufboss_update -k 30 -r -b 1000000000 -o bufboss_out/build --add-files data/coli12_build.txt
./bufboss/bin/bufboss_update -k 30 -r -b 0.05 -i bufboss_out/build/ --add-files data/coli12_add.txt -o bufboss_out/add/
./bufboss/bin/bufboss_update -k 30 -r -b 0.05 -i bufboss_out/build/ --del-files data/coli12_del.txt -o bufboss_out/del/
./bufboss/bin/bufboss_update -k 30 -r -b 0.05 -i bufboss_out/build/ --add-files data/coli12_add.txt --del-files data/coli12_del.txt -o bufboss_out/adddel/
