from socket import *
from struct import *
import pickle
import sys
import select
import time
import random


'''Taking in command line arguments. 
   Here argv[0] is the filename, 
   argv[1]=serverport given as 7735 
   argv[2] is the file the data is to be trasferred to
   argv[3] is the probability of error generation'''

sport = int(sys.argv[1])
fileName = str(sys.argv[2])
error_gen = float(sys.argv[3])

if len(sys.argv) != 4:
    print "Usage: python server <port#> <file-name> <p>"
    sys.exit()

'''UC I: standard checksum calculation for udp as mentioned in the client'''
def carry_around_add(a, b):
    c = a + b
    return (c & 0xffff) + (c >> 16)

def checksum(msg):
    if (len(msg) % 2) != 0:
        msg += "0"

    s = 0
    for i in range(0, len(msg), 2):
        w = ord(msg[i]) + (ord(msg[i+1]) << 8)
        s = carry_around_add(s, w)
    return ~s & 0xffff

'''UC II: sequence_exp is the packet with a particular sequence number the server expects to receive, read_file reads the given file
   acknow is the respective acknowledgment
   '''
def receive():
    global sequence_exp, acknow
    try:
        read_file = open(fileName, 'w')
    except IOError:
        print "Failed to open ", fileName
        sys.exit()
    '''UC-II: ensuring the correct packet with the expected sequence number is received'''
    while True:
        try:
            ready = select.select([serverSocket], [], [], timeout)
            if ready[0]:
                unserialized, address = serverSocket.recvfrom(4096)


            elif sequence_exp == 0:
                continue

            else:
                serverSocket.close
                read_file.close()
                sys.exit(0)

        except KeyboardInterrupt:
            print "\n Interrupted"
            serverSocket.close
            read_file.close()
            sys.exit(0)

        '''unserialized=decapsulating various packet fields'''
        unserialized = pickle.loads(unserialized)

        '''in case of checksum failure, print the following'''
        if unserialized['checksum'] != checksum(unserialized['info']):
            print "Failed-checksum"
            continue


        if sequence_exp != unserialized['sequence']:
            continue

        '''generate is the random probabilistic error generated '''
        generate = random.random()
        if generate <= error_gen:
            print "Packet loss, sequence number =", unserialized['sequence']
            continue

        '''In case a packet is successfully received from a client, 
           an acknowledgement for the packet that includes the next packet
           expected to be received is sent back to the client'''
        acknow['sequence'] = unserialized['sequence']
        acknow['allzeros'] = 0
        acknow['description'] = ack_recv

        acknowPickle = pickle.dumps(acknow)
        serverSocket.sendto(acknowPickle, (address[0], cport))
        sequence_exp =sequence_exp+ 1

        '''UC III: if all the usecases above work fine, proceeding to write data into the file named and 
           taken in from argv[2] from the command line input'''
        read_file.write(unserialized['info'])
    '''sport=serverport
       cport=clientport
       ack_recv=acknowledgement as specified in the question
       packet is the list representing the packet prepared on the client end which is to deserilaized
       acknow is the list representing the acknowledgement received for each packet sent'''
if __name__ == "__main__":
    sport = 7735
    cport = 7736
    ack_recv = 0b1010101010101010
    timeout = 4
    serv = gethostname()
    serverSocket = socket(AF_INET, SOCK_DGRAM)
    serverSocket.bind((serv, sport))
    serverSocket.setblocking(0)
    packet = {}
    acknow = {}
    sequence_exp = 0
    receive()
