#!/usr/bin/python3

import socket, time, sys, struct

BUFSIZE=4096
WORDS="/home/spa/g/org/ru_hacking_2013/level_5/words"

cache = {0:0, 1:1} 

def login(ip, port, password):
    """ Login to the server, authenticate and return the socket. """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ip, port))
    
    login_header = s.recv(BUFSIZE)
    if login_header != b'OK\tWelcome to the RU Hacking Contest QUIZ server. You seem to be far along...':
        print("Did not get expected server header.")
        print("got: %s)" % login_header)
        sys.exit(1)

    print("- Connected")
    
    auth_header = s.recv(BUFSIZE)
    if auth_header != b'\nOK\tPlease enter the access word.\n':
        print("Did not get the authentication question!")
        print("got: %s" % auth_header)
        sys.exit(1)
    
    # Ok, perform login.
    p = ("%s\n" % password).encode()
    s.send(p)
    auth = s.recv(BUFSIZE)
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

    response = sock.recv(BUFSIZE)
    if response != b'OK\tCorrect!':
        print("-- Not the correct answer")
        print("Got: %s" % response)
        sys.exit(1)
        
    print("-- Correct")

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
    

def process_fib_question(sock, question):
    answer = find_next_fib(int(question))
    
    print("-- Sending answer %s" % answer)
    sock.send( ("%s\n" % answer).encode() )

    response = sock.recv(BUFSIZE)
    if response != b'OK\tCorrect!':
        print("-- Not the correct answer")
        print("Got: %s" % response)
        sys.exit(1)
        
    print("-- Correct")

    return sock


if __name__ == "__main__":
    wordlist = read_words(WORDS)

    sock = login('hacking.ru.is', 1337, 'MELODY')
    
    while True:
        chunk = sock.recv(BUFSIZE)
        print("- received chunk: %s" % chunk)

        q = parse_question(chunk)

        if is_number(q):
            print("- Processing fib question %s" % q)
            process_fib_question(sock, q)
        else:
            print("- Processing word question %s" % q)
            process_word_question(sock, q, wordlist)
    


