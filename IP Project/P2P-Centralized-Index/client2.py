'''
some references 
http://effbot.org/zone/thread-synchronization.htm
https://www.tutorialspoint.com/python/python_networking.htm
http://stackoverflow.com/questions/2846653/how-to-use-threading-in-python

Opensource code from GITHUB was referred: https://github.com/adamgillfillan/p2p

'''


import socket
import cPickle as pickle 
import time
import os
import platform 
import threading


global myPort, serverPort, serverIp, hostname, OpSys

myPort = 65002
serverPort = 7734
serverIp = socket.gethostbyname(socket.getfqdn())

myVersion = 'P2P-CI/1.0'
clientSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
host = '127.0.0.1' 
#clientSocket.bind((host, myPort))
hostname = host
OpSys = platform.system()

def sendfile(rfc_num):
   
    
    path = os.getcwd() + '\\rfc2'
    filename = ''
    print 'rfc_num' , rfc_num
    for file1 in os.listdir(path):
        #print file1[0:4]
        print file1[0:4]
        if (file1[0:4] == rfc_num):
            filename = os.getcwd() + '\\rfc2\\' + file1 
           
    print 'fileame ', filename        
    #OpSys = platform.system()
    currTime = time.strftime("%a, %d %b %Y %X %Z")
    #path = os.getcwd()
    
    '''
    if OpSys == 'Windows':
        filename = "rfc\\" + filename 
    else:
        filename = "rfc/" + filename
    '''
    rfc_txt = ((open(filename, 'r')).read())
    
    rfc_last_modified = time.ctime(os.path.getmtime(filename)) #os.getcwd()+ '\\rfc2\\' + txt
    rfc_length = os.path.getsize(filename)    #os.getcwd()+ '\\rfc2\\' + txt
    print rfc_length
    resp_msg = 'P2P-CI/1.0 '+ '200 OK' + '\n' \
              'Date: ' + currTime + "\n"\
              "OS: " + (OpSys)+"\n"\
              "Last-Modified: " + rfc_last_modified + "\n"\
              "Content-Length: " + str(rfc_length) + "\n"\
              "Content-Type: text/text \n"
              
    print resp_msg
    print rfc_txt
    
    return resp_msg, rfc_txt, rfc_length



def get_RFC_details():              #Reference Stack Overflow http://stackoverflow.com/questions/3964681/find-all-files-in-a-directory-with-extension-txt-in-python
    path = os.getcwd() + '\\rfc2'
    rfc_detail = []
    for file1 in os.listdir(path):
        if file1.endswith(".txt"):
            rfc_detail.append(   [   file1[0: file1.index('_')], file1[file1.index('_')+1:file1.index('.')] ] )
    return rfc_detail    
    
       
def check_rfc(rfc_num):
    path = os.getcwd() + '\\rfc2'
    filename = ''
    for file1 in os.listdir(path):
        #print file1[0:4]
        if (file1[0:4] == rfc_num):
            filename = os.getcwd() + '\\rfc2\\' + file1 
    #filename =os.getcwd() + 'rfc\\' + rfc_num + '.txt'
    return os.path.isfile(filename)
         
class console_app_thread (threading.Thread):
    
    def __init__(self):
        threading.Thread.__init__(self)
        
        
    def run(self):
        
        global myPort
        
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((serverIp,serverPort))
        print (s.recv(8192))
        #Registration - send port number, RFC no and RFC Title as pickle
        temp_str = [myPort, get_RFC_details(), hostname]
        print 'Registration with server'
        print temp_str, '\n'
        s.sendall(pickle.dumps(temp_str)) #sending pickled []
        
        while True:
            
            #Get User input on what to do
            usr_ip_mode = raw_input('Enter the mode to enter:   1.P2S    2.P2P  ')
            
            if (usr_ip_mode == 'P2S'):
                
    
                
                while True:
                    
                    usr_ip = raw_input('Enter your input'  '\n' '1.ADD'   '\n' '2.LIST' '\n' '3.LOOKUP' '\n' '4.EXIT ' '\n')
                    
                    if (usr_ip == 'ADD'):
                        usr_ip_rfc_no  = raw_input ('Enter the RFC Number:')
                        usr_ip_rfc_title = raw_input ('Enter the RFC Title: ')  
                        temp_list = [['ADD', 'RFC', usr_ip_rfc_no, myVersion],['Host: ', hostname], ['Port: ', myPort], ['Title: ', usr_ip_rfc_title]]
                        s.sendall(pickle.dumps(temp_list))
                        
                        #To print the requets message
                        
                        temp_list = [['ADD', 'RFC', usr_ip_rfc_no, myVersion],['Host: ', hostname], ['Port: ', str(myPort)], ['Title: ', usr_ip_rfc_title]]
                        temp_str = ''
                        for element in temp_list:
                            new_str = ' '.join(element)
                            temp_str = temp_str  + new_str + '\n'
                        print 'Request to server.....'
                        print temp_str, '\n'
                        
                        #Response from server
                        'Response from server....'
                        print (pickle.loads(s.recv(8192)))
                         
                        
                    elif (usr_ip == 'LIST'):
                    
                        '''
                        LIST ALL P2P-CI/1.0
                        Host: thishost.csc.ncsu.edu
                        Port: 5678
                        '''
                        temp_list = [['LIST' ,'ALL' , myVersion], ['Host:', hostname],['Port:' , myPort]] #send the LIST command to server 
                        s.sendall(pickle.dumps(temp_list))
                        
                        #To print the requets message
                        
                        temp_list = [['LIST' ,'ALL' , myVersion], ['Host:', hostname],['Port:' , str(myPort)]]
                        temp_str = ''
                        for element in temp_list:
                            new_str = ' '.join(element)
                            temp_str = temp_str  + new_str + '\n'
                        print 'Request to server.....'
                        print temp_str, '\n'
                        
                        #Response from server
                        print 'Response from server....'
                        print s.recv(8192) 
                        
                    elif (usr_ip == 'LOOKUP'):
                        usr_ip_rfc_no  = raw_input ('Enter the RFC Number:')
                        usr_ip_rfc_title = raw_input ('Enter the RFC Title:')
                        '''
                        LOOKUP RFC 3457 P2P-CI/1.0
                        Host: thishost.csc.ncsu.edu
                        Port: 5678
                        Title: Requirements for IPsec Remote Access Scenarios
                        '''
                        temp_list = [['LOOKUP', 'RFC', usr_ip_rfc_no, myVersion], ['Host:', hostname], ['Port:' , myPort ], ['Title:', usr_ip_rfc_title]]
                        s.sendall(pickle.dumps(temp_list))
                        
                        #To print the requets message
                        
                        temp_list = [['LOOKUP', 'RFC', usr_ip_rfc_no, myVersion], ['Host:', hostname], ['Port:' , str(myPort) ], ['Title:', usr_ip_rfc_title]]
                        temp_str = ''
                        for element in temp_list:
                            new_str = ' '.join(element)
                            temp_str = temp_str  + new_str + '\n'
                        print 'Request to server.....'
                        print temp_str, '\n'
                        
                        #Response from server
                        print 'Response from server....'
                        print (pickle.loads(s.recv(8192)))
                        
                    elif (usr_ip == 'EXIT'):
                        s.close()
                        break
                    else:
                        print ('Invalid Command' + '\n')
                        continue
                            
                        
            elif (usr_ip_mode == 'P2P') :
                while True: 
                    usr_ip = raw_input('Enter your input'  '\n' '1.GET' '\n' '2.EXIT ' '\n')
                    if (usr_ip == 'GET') :
                        clientIp = raw_input ('Enter Client IP: ')
                        clientPort = input ('Enter Client port: ') 
                        rfc_req = raw_input ('Enter the RFC Number: ')
                        rfc_req_title = raw_input('Enter the RFC Name: ')
                    
                        try:
                            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            s.connect((clientIp,clientPort))
                            '''
                            GET RFC 1234 P2P-CI/1.0
                            Host: somehost.csc.ncsu.edu
                            OS: Mac OS 10.4.1
                            '''
                            temp_list = [['GET' ,'RFC' ,rfc_req, myVersion],['Host:', hostname],['OS:', OpSys ]]
                            s.sendall(pickle.dumps(temp_list))
                            
                            #To print request message
                            
                            temp_str = ''
                            for element in temp_list:
                                new_str = ' '.join(element)
                                temp_str = temp_str  + new_str + '\n'
                            print 'Request to server.....'
                            print temp_str, '\n' 
                            
                            #Response from peer
                            print 'Response from server....'
                            resp_msg = pickle.loads(s.recv(8192))
                            print resp_msg
                            resp_msg_lines = resp_msg.split('\n')
                            #print response1.split('\n')
                            rfc_size = int(resp_msg_lines[4].split(': ')[1]) #Extract RFC file size from the response msg
                            
                            parts = []    #Reference code snippet referred from Stack overflow
                            bytes_recv = 0
                            while bytes_recv < rfc_size:
                                part = s.recv(min(rfc_size - bytes_recv, 2048))
                                parts.append(part)
                                bytes_recv = bytes_recv + len(part)

                            rfc_txt = b''.join(parts)
                            print rfc_txt
                            
                            filename = os.getcwd() + '\\rfc2\\' + rfc_req+ '_' +rfc_req_title + ".txt"
                            (open(filename, 'w+')).write(rfc_txt)
                        
                        
                        except socket.error, e:
                            print ('Could not connect')
                            continue 
                    elif(usr_ip == 'EXIT') :
                        s.close()
                        break
                            
            else:
                print('Invalid mode, Please re-enter')   
          
class p2p_upload_thread(threading.Thread):
    
    def __init__(self):
        threading.Thread.__init__(self)
    
    def run (self):
        #print 'came to upload port_thread' '\n'
        global myPort, myVersion
        client_upload_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        host = '127.0.0.1'
        client_upload_socket.bind((host, myPort)) 
        client_upload_socket.listen(5)
        while True:
            #print 'came here'
            peer_conn, peer_addr = client_upload_socket.accept()
            '''
            GET RFC 1234 P2P-CI/1.0
            Host: somehost.csc.ncsu.edu
            OS: Mac OS 10.4.1
            '''
            print 'Request from peer...'
            peer_msg = pickle.loads(peer_conn.recv(8192))
            print (peer_msg)
            
            if (peer_msg[0][3] == myVersion):
                print   'Version match' 
                if (peer_msg[0][0] == 'GET'):
                    if check_rfc(peer_msg[0][2]): #check if rfc is available
                        #Rfc is avalable 
                        print 'RFC Available'
                        resp_msg, rfc_txt, rfc_size= sendfile(peer_msg[0][2]) #Get the response for the RFC number, returns rfc data if available otherwise returns error 
                        print 'Response to peer...'
                        print 'Response Msg' , resp_msg
                        peer_conn.sendall(pickle.dumps(resp_msg))
                        msg_sent = 0
                        while msg_sent < rfc_size:
                            sent = peer_conn.send(rfc_txt[msg_sent:])
                            msg_sent = msg_sent + sent
                    
                    else:
                        #RFC is not available  
                        print 'Response to peer...'
                        temp_str = ('P2P-CI/1.0 '+  '404 Not Found' + "\n"\
                        "Date:" + time.strftime("%a, %d %b %Y %X %Z") + "\n"\
                        "OS: "+str(platform.system())+"\n"  ) 
                        
                        peer_conn.sendall(pickle.dumps(temp_str))          
            else:
                #Send error msg when version not supported 
                
                temp_str = ('P2P-CI/1.0 '+  '505 P2P-CI Version Not Supported' + "\n"\
                        "Date:" + time.strftime("%a, %d %b %Y %X %Z") + "\n"\
                        "OS: "+str(platform.system())+"\n"  )
                peer_conn.sendall(pickle.dumps(temp_str))

    
                
            
                   
thread1 = console_app_thread()
thread2 = p2p_upload_thread()

thread1.start()
thread2.start()
            