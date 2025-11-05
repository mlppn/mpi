.POSIX:
.SUFFIXES: .c .o
$(CFLAGS) = -Wall -Wextra -g

.c.o:
	$(CC) $(CFLAGS) -c $<

tp: main.o add.o
add.o: add.c add.h
main.o: main.c add.h
clean:
	rm -f *.o tp
.PHONY: clean
tp: main.o add.o
	cc -o tp main.o add.o
add.c: add.h
	cc -c add.c


