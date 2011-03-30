import socket
import threading
import array
import sys

# WARNING: THIS ASSUMES YOUR INTS ARE 4 BYTES LONG
# TODO: FIX THIS ^^^

class mysocket:
    # from http://docs.python.org/howto/sockets.html

    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self, host, port):
        self.sock.connect((host, port))

    def mysend(self, msg):
        totalsent = 0
        while totalsent < len(msg):
            sent = self.sock.send(msg[totalsent:])
            if sent == 0:
                raise RuntimeError("socket connection broken")
            totalsent = totalsent + sent

    def myclose(self):
        self.sock.close()

    def viconreceive(self):
        # get header
        msg = self.myreceive(2*4)
        header = array.array('I',msg)
        if header[0] == 1:
            # info packet
            msg = self.myreceive(1*4)
            length = array.array('I',msg)
            strs = []
            for i in xrange(length[0]):
                msg = self.myreceive(1*4)
                strlen = array.array('I',msg)
                msg = self.myreceive(strlen[0])
                strs.append(msg)
            return strs 
        elif header[0] == 2:  
            # data packet
            msg = self.myreceive(1*4)
            length = array.array('I',msg)
            msg = self.myreceive(length[0]*8)
            body = array.array('d',msg)
            return body
        else:
            # something else
            return header

    def myreceive(self, msglen):
        msg = ''
        while len(msg) < msglen:
            chunk = self.sock.recv(msglen-len(msg))
            if chunk == '':
                raise RuntimeError("socket connection broken")
            msg = msg + chunk
        return msg

def processStream(s,info):
    ###########################################
    #### you might want to edit this part! ####
    ###########################################

    #STREAMS_YOU_WANT = [32,33,34]
    STREAMS_YOU_WANT = [i for (i,n) in enumerate(info) if "armRightUp <a" in n]

    ###########################################
    ###########################################

    while KEEP_LISTENING:
        data = s.viconreceive()
        for i in STREAMS_YOU_WANT:
            print info[i] , ": " , data[i], "  ", 
        print


print ">> Connecting..."
s = mysocket()
s.connect("10.0.0.102", 800)

print ">> Requesting stream info..."
init = array.array('I',[1,0]).tostring()
s.mysend(init)

print ">> Receiving stream info..."
info = s.viconreceive()

if len(sys.argv) > 1 and sys.argv[1] == "-l":
    print "Available streams:"
    print "   " + "\n   ".join(["(%d) %s" % (i,n) for i,n in enumerate(info)])
    sys.exit(0)

print ">> Starting streams..."
init = array.array('I',[3,0]).tostring()
s.mysend(init)

global KEEP_LISTENING
KEEP_LISTENING = True
listenThread = threading.Thread(target = processStream, args = (s,info))
listenThread.start()

try:
    raw_input(" *** Press ENTER to stop! ***")
except KeyboardInterrupt:
    pass

KEEP_LISTENING = False
listenThread.join()

print ">> Stopping streams..."
init = array.array('I',[4,0]).tostring()
s.mysend(init)

print ">> Disconnecting..."
s.myclose()

