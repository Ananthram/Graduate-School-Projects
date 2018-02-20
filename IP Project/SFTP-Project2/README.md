Pls see the [report](https://github.com/Ananthram/Graduate-School-Projects/blob/master/IP%20Project/SFTP-Project2/Report_Readme.pdf) for instructions on running the code in a well formated form


README
• The server file is server.py and the client file is client.py
• The file used for transfer is named Sample.pdf
• The file on the server to which it is written is named create.txt
• The checksum code is a standard code we obtained form:
(http://stackoverflow.com/questions/1767910/checksum-udp-calculation-python)
• The other resources used were:
https://github.com/codyharrington/python-udp-filetransfer
https://github.com/confuzzed03/Python-UDP-File-Transfer
https://github.com/blasrodri/File-Transfer-Python
https://github.com/gibsjose/UDPFileTransfer
https://docs.python.org/2/library/select.html
http://andrewtrusty.com/2006/11/22/reliable-udp-file-transfer-2/
• Further, there were some very standard functions and data fields that were
mentioned in the specification of the question like use of rdt_send() and data and
acknowledgement fields. We directly used them as per the instructions
• We varied the timeout values to check various scenarios (on both server and client)
• Both the server and client codes are run according to the following use cases:
Client:
(i) Take in the arguments from the command line
(ii) Checksum calculation as per the standard code
(iii) To create a packet, generate various fields and then append them in a serial
manner. This appending was done using the ‘pickle’ serializer in python
(iv) Once the packet is prepared, the transmission of this packet is done using
the rdt_send() function, which checks for various conditions as specified in
the Go-Back-N protocol
Server:
(i) The server takes in the arguments as specified in the question
(ii) The server is the listener whereas the client is the sender
(iii) The server creates the file (where data is to be written/transferred) on the
fly as specified in the input (as command line arguments)
(iv) The checksum code is the same as used in the client end
(v) The server is responsible for generating errors (packet losses) using
probabilistic packet loss generator)
• To run the server first: python server.py server port number (7735) file to be
created (create) probabilistic error/packet loss generator (p=between 0 and 1)
Hence, command: python server.py 7735 create.txt 0.05
• To run the client: python client.py hostname(local/remote host) server port
number (7735) file to be transmitted (Sample.pdf) window-size(N) MSS
Hence, command: python client.py localhost 7735 Sample.pdf 64 1000
P.S:
<Localhost>: specifies hostname of device being run on
we obtained it using socket.hostname()
Each program- the server and the client is divided into several use cases and the logic for each of the use
case is commented in the code with a marking, UC and explained:
Client:
UC I: Read the arguments from the command line
UC II: Preparation of packet- append various fields (serialize) using Pickle module. The specifications of
the various fields are given in the project description
UC III: call the function packet_generator() for preparation of packet with various fields
buffer the packet and send to socket for transfer
check if the correct acknowledgement is received
Server:
UC I: On receiving a packet, ensure the checksum for correctness of the packet using the checksum
code
UC II: On receiving the packet, check if the packet is in sequence
UC III: writing data into a specified file
