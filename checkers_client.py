from socket import socket, AF_INET, SOCK_STREAM
from sys import argv, stdout, exit
from threading import Thread
import random                                                      #IMPORT LIBRARIES
import os
import logging

buffer_size = 8192
connected = False
logging.basicConfig(level=logging.INFO, filename='checkersclient.log', format='[%(levelname)s] %(asctime)s %(threadName)s %(message)s',)


def recv_all(sock, server_IP, crlf):

    try:
        while True:
            data = ""
            while not data.endswith(crlf):
                data = data + sock.recv(1)
            print str(data[:-4])
            stdout.flush()
            #return data[:-4]
    except:
        connected = False
        exit(1)


def send_to_server(sock, server_IP):
    try:
        while True:
            data = ""
            data = raw_input()
            data = data + "\r\n\r\n"
            sock.sendall(data)
    except:
        connected = False
        exit(1)
    

def main(argv):
    server_IP_addr = argv[1]                    #IP Serwera
    #server_IP_addr = '192.168.0.1'

    server_port = int(argv[2])                  #Port Serwera
    #server_port = 9528
    
    sock = socket(AF_INET, SOCK_STREAM)
    sock.connect((server_IP_addr,server_port))
    connected = True
    #data = raw_input('> ')
    send_thread = Thread(target=send_to_server, args=(sock, server_IP_addr))            #Wysylanie do serwera
    send_thread.start()
    recv_thread = Thread(target=recv_all, args=(sock, server_IP_addr, "\r\n\r\n"))          #Odbieranie z serwera
    recv_thread.start()

    try:
        while True:
            if (not connected):
                exit(1)
    except (KeyboardInterrupt, SystemExit):
        stdout.flush()
        print '\nConnection to server closed.'
        logging.info("Connection to server closed")
    
main(argv)
