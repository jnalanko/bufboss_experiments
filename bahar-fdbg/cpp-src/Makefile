
.PHONY: fdbg-build-jarno fdbg-add-jarno fdbg-del-jarno
all: fdbg-build-jarno fdbg-add-jarno fdbg-del-jarno

#bds: BuildDataStructure.cpp formatutil.cpp TestUtil.cpp FDBG.cpp
#	g++ -O3  -std=c++11 -DBOOST_LOG_DYN_LINK BuildDataStructure.cpp -o bds -L/s/apu/a/homes/baharpan/boost/lib -I/s/apu/a/homes/baharpan/boost/include  -lboost_filesystem -lboost_log -lboost_system -lboost_thread  -l pthread
#format: test_format.cpp
#	g++ -O3  -std=c++11 test_format.cpp -o tf -l boost_log -l pthread -l bf
test: BuildDataStructure.cpp formatutil.cpp TestUtil.cpp FDBG.cpp
	g++ -O3  -std=c++11 -DBOOST_LOG_DYN_LINK BuildDataStructure.cpp -o bds_test -L/s/apu/a/homes/baharpan/boost/lib -I/s/apu/a/homes/baharpan/boost/include  -lboost_filesystem -lboost_log -lboost_system -lboost_thread  -l pthread
test-jarno:
	g++ -O3  -std=c++17 test.cpp -o test-jarno -l boost_log -l boost_system -l pthread -DNDEBUG

fdbg-build-jarno:
	g++ -O3  -std=c++17 fdbg-build-jarno.cpp -o fdbg-build-jarno -l boost_log -l boost_system -l pthread -DNDEBUG -march=native

fdbg-add-jarno:
	g++ -O3  -std=c++17 fdbg-add-jarno.cpp -o fdbg-add-jarno -l boost_log -l boost_system -l pthread -DNDEBUG -march=native

fdbg-del-jarno:
	g++ -O3  -std=c++17 fdbg-del-jarno.cpp -o fdbg-del-jarno -l boost_log -l boost_system -l pthread -DNDEBUG -march=native

fdbg-query-jarno:
	g++ -O3  -std=c++17 fdbg-query-jarno.cpp -o fdbg-query-jarno -l boost_log -l boost_system -l pthread -DNDEBUG -march=native

#readsplit: ReadSplit.cpp
#	g++ -O3 -std=c++11 ReadSplit.cpp -o readsplit -l boost_log -l pthread
#countreads: CountReads.cpp
#	g++ -O3 -std=c++11 CountReads.cpp -o countreads -l boost_log -l pthread
clean:
	rm bds *.bin
