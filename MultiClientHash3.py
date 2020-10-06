import socket
import time
from threading import Thread
import struct
TCP_IP = '34.71.37.77'
TCP_PORT = 65432
BUFFER_SIZE = 1024


def recvall(sock, count):
    buf = b''
    while count:
        newbuf = sock.recv(count)
        if not newbuf:
            return None
        buf += newbuf
        count -= len(newbuf)
    return buf


def send_one_message(sock, data):
    length = len(data)
    sock.sendall(struct.pack('!I', length))
    sock.sendall(data)


def recv_one_message(sock):
    lengthbuf = recvall(sock, 4)
    length, = struct.unpack('!I', lengthbuf)
    return recvall(sock, length)


class ClientThread(Thread):
    def __init__(self, id):
        Thread.__init__(self)
        print(" New thread started at "+str(time.time())+":"+str(TCP_PORT))
        self.id = id

    def run(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((TCP_IP, TCP_PORT))
        recived_f = 'imgt_thread' + \
            str(self.id) + str(time.time()).split('.')[0] + '.jpg'
        with open(recived_f, 'wb') as f:
            print('file opened')
            while True:
                # print('receiving data...')
                data = recv_one_message(s)
                print('data=%s', (data))
                if not data:
                    f.close()
                    print('file close()')
                    break
                # write data to a file
                f.write(data)

        print('Successfully get the file')
        s.close()
        print('connection closed')


for i in range(25):
    ClientThread(i).start()
