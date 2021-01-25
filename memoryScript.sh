echo "" > mem.log
while true; do
ps -C merge -o pid=,%mem=,rss= >> mem.log
#gnuplot gnuplot.script
sleep 0.1
echo "logged memory"
done
