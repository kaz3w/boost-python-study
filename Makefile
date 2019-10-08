CPLUS_INCLUDE_PATH:=/usr/include/python2.7

INCLUDES = \
	-I /usr/include/ \
	-I /usr/include/boost/ \
	-I /usr/include/python2.7/


LIBS = \
	-lboost_python \
	-lboost_numpy


TARGET=mylib.so
TARGET_SAMPLE=mylib_sample.so


all: $(TARGET) $(TARGET_SAMPLE)


$(TARGET): mylib.cpp mylib.h Makefile
	g++ -DPIC -shared -fPIC $(INCLUDES) mylib.cpp -o $(TARGET) $(LIBS)


TARGET_SAMPLE_LIBS = \
	-lboost_python \
	-lboost_numpy \
	-luvc \
	-lopencv_highgui \
	-lopencv_core


$(TARGET_SAMPLE): mylib_sample.cpp mylib_sample.h Makefile
	g++ -DPIC -shared -fPIC $(INCLUDES) mylib_sample.cpp -o $(TARGET_SAMPLE) $(TARGET_SAMPLE_LIBS)


test:
	python test_mylib.py
	python test_mylib_sample.py

test2:
	python test_mylib_sample.py



clean:
	rm -f *.o $(TARGET) $(TARGET_SAMPLE)
