from socket import *
from struct import *
import pickle
import sys
import select
import time

'''Taking in 6 inputs from the console out of which argv[0] is the filename(.py) itself'''
if len(sys.argv) != 6:
    print "python client <server-host-name> <server-port#> <file-name> <N> <max_segment>"
    sys.exit()

sport = 7735
'''UC1: The various fields as per the command line inputs'''
serv = str(sys.argv[1])
sport = int(sys.argv[2])
fileName = str(sys.argv[3])
window = int(sys.argv[4])
max_segment = int(sys.argv[5])

'''The standard checksum generator which is checked on the listener/server end on reception of each packet.
   The various arguments used are specific to the named checksum techniques-carry around add
   Source of the checksum part of the code is referenced in the readme section of the report'''
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


def packet_generator(info):
    sequence = 0
    packets = []
    trans_packet = 0
    '''Clause 1:Selects the packet to be prepared based on what is minimum- the MSS or the length of the
       data in the file we read-what is already transmitted'''
    lenofpkt = min(max_segment, len(info) - trans_packet)

    '''UC II:Here we are concerned with preparing a packet with the various fields it has to hold. 
       "sequence" indicates the sequence number .
       "checksum" is a standard mechanism done on both-the server and the client end. It is run on 
       "Pickle" module to serialize various parts of the packet and sequentially arrange the specified fields
       "description" is the type of packet"
       "lenofpkt gives the length of packet"
       "trans_packet is the transmitted packet
       "info contains the data" 
        The packet is prepared only if it is possible for the amount of remainder data to be transmitted
        be greater than 0 so that the Clause 1 can be fulfilled'''
    while lenofpkt > 0:

        packet['sequence'] = sequence
        packet['checksum'] = checksum(info[trans_packet:trans_packet + lenofpkt])
        packet['description'] = info_send
        packet['info'] = info[trans_packet:trans_packet + lenofpkt]
        packet['ack'] = False
        dataserialized = pickle.dumps(packet)
        packets.append(dataserialized)
        trans_packet =trans_packet+ lenofpkt
        lenofpkt = min(max_segment, len(info) - trans_packet)
        sequence =sequence+ 1

    return packets

    '''UC III:rdt_send() is concerned with receiving data to be sent.
       "packets" parameter calls the function packet_generator() which checks the length of the packet
       "buffered" parameter checks if the data packet which is prepared is properly buffered to be sent
       (as per specifications in the question)
       "ack" and "unack" parameters specify the third responsibilty of the function which ensures 
        proper acknowledgement of the packet which is sent'''
def rdt_send(info):

    packets = packet_generator(info)
    '''"nak" is negative acknowledgement received in case of lost packets 
       "firstnak" is acknowledgment(negative) which is cumulative in nature, in the sense, the nak for a packet with 
        sequence number 51 which was lost would be 51 and in case of the loss of even the next packet the negative 
        acknowledgement needs to be incremented for the next, just like sequence numbers'''

    firstnak = 0
    nak = 0

    '''sendto functionality is used serve data to the port of the server. 
       Hence, the binding-second parameter of the sendto function
       signifies that. The data sent is the packet prepared, referred to as packets.'''

    while firstnak < len(packets):


        if nak < window and (nak + firstnak) < len(packets):
            sock.sendto(packets[firstnak + nak], (serv, sport))
            nak =nak+ 1
            continue

            '''for the given sequence number an ack packet with the next expected packet with the consecutive seq num
               interface system call is done using the select module, TIMEOUT is standard hwere id we do specify
               the first three parameters, they wait for the specified TIMEOUT period'''
        else:
            buffered = select.select([sock], [], [], timeout)
            '''when the buffering of the packet is completed then the data is ready to be received on the socket'''
            if buffered[0]:
                ackPacket, address = sock.recvfrom(4096)
                ackPacket = pickle.loads(ackPacket)

            else:
                print "Timeout, sequence number =", firstnak
                nak = 0
                continue


            if ackPacket['description'] != ack_recv:
                continue


            if ackPacket['sequence'] == firstnak:
                firstnak =firstnak+ 1
                nak=nak- 1
            else:
                nak = 0
                continue

    print "File transferred"
    sock.close()

''' reading: this function is basically used to read a file from a given source. 
    The file is given as a command line argument. 
    We try and read the function and if there is specifically inability to read to display/write the file, we go in
    for an exception. 
    In case the file has no content in it, the test case results to an empty file output displayed on the console '''


def file_input():
    try:
        fp = open(fileName, 'r')
        info = fp.read()
        fp.close()
    except IOError:
        print "Failed to open ", fileName
        sys.exit()

    if info == "":
        print "Empty file"
        sys.exit()

    start= time.time()
    rdt_send(info)
    print "Time for transfer: ", time.time()-start
    '''These are the fields specified in the question. 
       TIMEOUT field is used as Python standard for the keepalive timer on the server end and 
       also retransmission timer in case of loss of packets on the or lack of acknowledgement on the sender's end '''
if __name__ == "__main__":
    info_send = 0b0101010101010101
    timeout = .4
    ack_recv = 0b1010101010101010
    client = gethostname()
    cport = 7736
    sock = socket(AF_INET, SOCK_DGRAM)
    sock.bind((client, cport))
    sock.setblocking(0)
    '''packet is the list/dict used which contains the serialized form of a single packet with various fields in it 
       as prepared in packet_generator() 
       acknow is the format for an acknowledgement packet'''
    packet = {}
    acknow = {}
    file_input()
