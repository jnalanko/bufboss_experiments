set -e
set -u

ls $PWD/coli3682/*.fna | shuf | head -n 12 > coli12.txt
head -n 6 coli12.txt > coli12_build.txt
head -n $(expr 6 + 3) coli12.txt | tail -n 3 > coli12_add.txt
head -n $(expr 6 + 3 + 3) coli12.txt | tail -n 3 > coli12_del.txt

ls $PWD/coli3682/*.fna | shuf | head -n 3682 > coli3682.txt
head -n 1842 coli3682.txt > coli3682_build.txt
head -n $(expr 1842 + 920) coli3682.txt | tail -n 920 > coli3682_add.txt
head -n $(expr 1842 + 920 + 920) coli3682.txt | tail -n 920 > coli3682_del.txt
