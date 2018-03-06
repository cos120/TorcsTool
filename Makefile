all: target

cc=g++
TorcsTool.o: TorcsTool.cpp
	$(cc) -c -fpic TorcsTool.cpp -o TorcsTool.o

target: TorcsTool.o
	$(cc) -shared -Wl,-soname,TorcsTool.so  TorcsTool.o -o TorcsTool.so

