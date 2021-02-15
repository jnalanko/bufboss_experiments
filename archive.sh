# Usage: give result tar file name as argument

if [ "$#" -ne 1 ]; then
    echo "Give result tar filename as parameter"
    exit
fi

tar -cvf $1 *_results
