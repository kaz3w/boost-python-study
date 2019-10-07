INCLUDES = \
	-I/usr/include \
	-I/usr/include/boost \
	-I/usr/include/python2.7
	
LIBS = \
	-lboost_python \
	-lboost_numpy

TARGET=mylib.so

all: clean $(TARGET)

$(TARGET): mylib.cpp Makefile
	g++ -DPIC -shared -fPIC $(INCLUDES) mylib.cpp  $(LIBS) -o $(TARGET) $(LIBS)

test:
	python test_mylib.py

clean:
	rm -f *.o $(TARGET)
