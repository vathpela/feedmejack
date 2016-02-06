
CC = gcc
CFLAGS = -Wall -Werror -Wsign-compare -g3

all : mill

mill : | libgrbl.h
mill : mill.c grbl.c
	$(CC) $(CFLAGS) -o $@ $^ -lpopt -lreadline
