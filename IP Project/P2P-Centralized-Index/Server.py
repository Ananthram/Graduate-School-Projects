

'''
some references 
http://effbot.org/zone/thread-synchronization.htm
https://www.tutorialspoint.com/python/python_networking.htm
http://stackoverflow.com/questions/2846653/how-to-use-threading-in-python

Opensource code from GITHUB was referred: https://github.com/adamgillfillan/p2p

'''




import socket

import cPickle as pickle
import threading

global peers, RFC 
peers = [] #Peers list  [[peer, uport], [peer, uport]]
RFC =[] #RFC list [[RFC no, RFC title, hostName],[RFC no, RFC title, hostName].....]

serverPort = 7734 #Server Well Known Port
serverSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM) #Creating a TCP socket
host = socket.gethostbyname(socket.getfqdn()) #get host name of server
#print host
serverSocket.bind((host,serverPort)) #Bind host and port number to socket
serverSocket.listen(5) 

print 'The server is ready to receive'

def resp_msg(status):
    if status == "200":
        phrase = "OK"
    elif status == "404":
        phrase = "Not Found"
    elif status == "400": 
        phrase = "Bad Request"
    msg = "P2P-CI/1.0 " + status + " " + phrase + "\n"
    return msg

def addPeer(peerList, host, uPort): 
    peerList.append([host, uPort])
    
def deletePeer(rfcList,peerList, peer ):
    global RFC, peers
    new_rfc_list = []
    new_peer_list= []
    
    for entry in rfcList:
        if (entry[2] != peer):
            new_rfc_list.append(entry)
            
    print new_rfc_list     
       
    for entry in peerList:
        if (entry[0] != peer):
            new_peer_list.append(entry)
    
    print   new_peer_list      
    RFC = new_rfc_list 
    peers = new_peer_list
 
 
   
def addRfc(rfcList, rfcDetails, host):   #addRfc(RFCList, [rfc_num,rfc_title], hostname)
    for entry in rfcDetails :
        rfcList.append([entry[0],entry[1],host])   # Append to RFC list an entry like [RFC no, RFC title, hostName]
    
def rfc_lookup(rfcList,peerList, rfc_no):
    temp = []
    for entry in rfcList :
        if (entry[0] == rfc_no):
            
            for peer in peerList:
                if (peer[0] == entry[2]):
                    temp.append([entry[2], peer[1]])
        
    return temp #Returns a list of peers with the mentioned rfc # Returns temp as [[peer, peerport], [peer,peerport]......]
        
def rfc_list(rfcList,peerList):
    #print ('Current RFC List', rfcList)
    #print ('Current peer List', peerList)
    '''
    P2P-CI/1.0 200 OK
    RFC 123 A Proferred Official ICP thishost.csc.ncsu.edu 5678
    '''
    temp_str='' #temp variable to store the return string 
    temp_peer_port = '' #temp variable to hold upload port
    
    for entry in rfcList:               #[[RFC no, RFC title, hostName],[RFC no, RFC title, hostName].....]
        for peer in peerList:
            if (entry[2] == peer[0]):
                temp_peer_port = peer[1]
                
        #print ('temp_str' , temp_str)
        #print entry 
        #print ('temp_peer_port',str(temp_peer_port)  )
        temp_str = (temp_str +'RFC ' + entry[0] +' '+ entry[1]+' ' + entry[2] +' '+ str(temp_peer_port) +' \n')
    #print temp_str    
    return temp_str  
        
   
class clientThread (threading.Thread):
    
    def __init__(self, conn, host):
        threading.Thread.__init__(self)
        self.conn = conn
        self.host = host[0]
        try :
            self.peerDetail_pickle = self.conn.recv(8192)               #receive port number, RFC no and RFC Title as pickle
            #print (self.peerDetail_pickle)
            self.peerDetail = pickle.loads(self.peerDetail_pickle)   # Convert peerDetail from pickle to list
            #print (self.peerDetail)
        except socket.error, e:
            print 'socket error....closing socket'
            self.conn.close()
            
    global peers, RFC
    
    def run(self): 
        try:
            threadLock.acquire()     #Acquire resources 
            #print 'SELF.HOST ---->' 
            #print self.host
            self.host = self.peerDetail[2]
            addPeer(peers, self.host, self.peerDetail[0]) # call addPeer func to add new peer to the peers list
            print 'New peer connected ', str(self.host), ',peer at port ', str(self.peerDetail[0])
            addRfc(RFC,self.peerDetail[1],self.host)    #Call addRfc func to add new rfc to rfcs list, (RFCList, [rfc no, rfc names], host name )
            threadLock.release() #release resources 
        
            while True: 
                msg_recv = self.conn.recv(8192)
                #print 'Received from client ' , msg_recv
                self.msg = pickle.loads(msg_recv) #msg is sent in the form of list
                print 'Received from client ', self.msg
            
                if (self.msg[0][0] == 'ADD'): # [ADD RFC 123 P2P-CI/1.0] /n [Host: thishost.csc.ncsu.edu] /n [Port: 5678] /n [Title: A Proferred Official ICP] 
                    threadLock.acquire()
                    #print [self.msg[0][2],self.msg[3][1]]
                    addRfc(RFC,[[self.msg[0][2],self.msg[3][1]]],self.host ) #adding the rfc details to RFC List   addRfc(RFCList, [rfc_num,rfc_title], hostname)
                    '''
                    Reply
                    P2P-CI/1.0 200 OK
                    RFC 123 A Proferred Official ICP thishost.csc.ncsu.edu 5678
                    '''
                    self.conn.sendall(pickle.dumps(resp_msg('200')  + 'RFC ' + self.msg[0][2] + ' ' +self.msg[3][1] + ' ' + self.msg[1][1] +' '+ str(self.msg[2][1])))
                    threadLock.release()
                
                elif (self.msg[0][0] == 'LOOKUP'): # [LOOKUP RFC 3457 P2P-CI/1.0] \n [Host: thishost.csc.ncsu.edu] \n [Port: 5678] \n [Title: Requirements for IPsec Remote Access Scenarios]
                    threadLock.acquire()
                    print 'came here'
                    lookup_result = rfc_lookup(RFC,peers,self.msg[0][2]) #call function to check if rfc available 
                    print lookup_result
                    threadLock.release()
                    
                    if not lookup_result:
                        self.conn.sendall(pickle.dumps(resp_msg('404')))
                    else:
                        '''
                        P2P-CI/1.0 200 OK
                        RFC 123 A Proferred Official ICP  available at host1 host2
                        '''                
                        str1 = ''
                        for entry in lookup_result:
                            '''
                            print 'str1', str1
                            print self.msg[0][2]
                            print self.msg[3][1]
                            print entry[0]
                            print entry[1]
                            '''
                            str1 = str1 + 'RFC ' + self.msg[0][2] + ' ' + self.msg[3][1] +' '+ entry[0] + ' ' + str(entry[1]) + '\n'
                            
                        self.conn.sendall(pickle.dumps(resp_msg('200') + (str1))) #  P2P-CI/1.0 200 OK \n RFC 123 A Proferred Official ICP  available at host1 host2
                
                elif (self.msg[0][0] == 'LIST'):
                    '''
                    P2P-CI/1.0 200 OK
                    RFC 123 A Proferred Official ICP thishost.csc.ncsu.edu 5678
                    RFC 6734 BGP EVPN MPLS somehost.bbd.edu 5697
                    '''
                    
                    threadLock.acquire()
                    list_result = rfc_list(RFC, peers)
                    threadLock.release()
                    
                    if not list_result:
                        self.conn.sendall(pickle.dumps(resp_msg('404') + 'No RFCs available'))
                        
                    else:
                        temp_str = resp_msg('200') + list_result
                        
                        print 'Now printing ' + temp_str 
                        self.conn.sendall(temp_str)      
                    
                    print 'PeerList', peers
                    
                else:
                    self.conn.sendall(resp_msg('400'))
                    
                    
        except (socket.error, EOFError):
            print 'socket error....closing socket....deleting peer'
            threadLock.acquire()
            deletePeer(RFC, peers, self.host )
            threadLock.release()
            print 'New RFC LIST' , RFC ,'\n' , 'New Peers list ' , peers
            self.conn.close()
                           
        
        
        



threadLock = threading.Lock()

while 1:
    #print 'came here'
    connectionSocket, addr = serverSocket.accept()
    #print connectionSocket
    #print addr
    connectionSocket.send('Connected to server')
    t = clientThread(connectionSocket, addr) #Call clientThread
    t.start()
    #print peers
    #print RFC
    #print 'bye' 
    #connectionSocket.close()