all: target

cc=g++
Torcs_tool.o: TorcsTool.cpp
	$(cc) -c -fpic TorcsTool.cpp -o Torcs_tool.o

target: Torcs_tool.o
	$(cc) -shared -Wl,-soname,Torcs_tool.so  Torcs_tool.o -o Torcs_tool.so

clean: 
	rm *.o
