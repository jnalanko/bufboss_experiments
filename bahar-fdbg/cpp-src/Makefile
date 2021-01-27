
#bds: BuildDataStructure.cpp formatutil.cpp TestUtil.cpp FDBG.cpp
#	g++ -O3  -std=c++11 -DBOOST_LOG_DYN_LINK BuildDataStructure.cpp -o bds -L/s/apu/a/homes/baharpan/boost/lib -I/s/apu/a/homes/baharpan/boost/include  -lboost_filesystem -lboost_log -lboost_system -lboost_thread  -l pthread
#format: test_format.cpp
#	g++ -O3  -std=c++11 test_format.cpp -o tf -l boost_log -l pthread -l bf
test: BuildDataStructure.cpp formatutil.cpp TestUtil.cpp FDBG.cpp
	g++ -O3  -std=c++11 -DBOOST_LOG_DYN_LINK BuildDataStructure.cpp -o bds_test -L/s/apu/a/homes/baharpan/boost/lib -I/s/apu/a/homes/baharpan/boost/include  -lboost_filesystem -lboost_log -lboost_system -lboost_thread  -l pthread
test-jarno: BuildDataStructure.cpp formatutil.cpp TestUtil.cpp FDBG.cpp
	g++ -O3  -std=c++17 test.cpp -o test-jarno -l boost_log -l boost_system -l pthread -I ../sux -DNDEBUG

#readsplit: ReadSplit.cpp
#	g++ -O3 -std=c++11 ReadSplit.cpp -o readsplit -l boost_log -l pthread
#countreads: CountReads.cpp
#	g++ -O3 -std=c++11 CountReads.cpp -o countreads -l boost_log -l pthread
clean:
	rm bds *.bin
