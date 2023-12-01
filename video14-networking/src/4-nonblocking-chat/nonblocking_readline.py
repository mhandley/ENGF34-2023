from fcntl import fcntl, F_GETFL, F_SETFL
from sys import stdin
from os import O_NONBLOCK

readbuffer = ""
def nonblocking_readline():
    global readbuffer
    #tty.setcbreak(stdin)

    # get flags associated with stdin
    fl = fcntl(stdin.fileno(), F_GETFL)

    # set the non blocking flag
    fcntl(stdin.fileno(), F_SETFL, fl | O_NONBLOCK)

    # try to read.  We'll get nothing if there's no character to read.
    c = stdin.read(1)
    while c:
        # add char to our receive buffer
        readbuffer += c
        if ord(c) == 127:
            # sort of handle deletion - really only works if echoing is turned off
            readbuffer = readbuffer[:len(readbuffer)-2]
        elif c == '\n':
            # if there's a newline, release the text
            newbuffer = readbuffer
            readbuffer = ""
            return newbuffer
        c = stdin.read(1)
    return ""
