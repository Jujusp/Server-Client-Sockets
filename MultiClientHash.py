import socket
import time
from threading import Thread
TCP_IP = '34.71.37.77'
TCP_PORT = 65432
BUFFER_SIZE = 1024


class ClientThread(Thread):
    def __init__(self, id):
        Thread.__init__(self)
        print(" New thread started at "+str(time.time())+":"+str(TCP_PORT))
        self.id = id

    def run(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((TCP_IP, TCP_PORT))
        recived_f = 'dicc' + \
            str(self.id) + str(time.time()).split('.')[0] + '.txt'
        with open(recived_f, 'wb') as f:
            print('file opened')
            while True:
                # print('receiving data...')
                data = s.recv(BUFFER_SIZE)
                print('data=%s', (data))
                if not data:
                    f.close()
                    print('file close()')
                    break
                # write data to a file
                f.write(data)

        # recived_f = 'imgt_thread' + \
        #    str(self.id) + str(time.time()).split('.')[0] + '.jpg'
        # with open(recived_f, 'wb') as f:
        #    print('file opened')
        #    while True:
        #        # print('receiving data...')
        #        data = s.recv(BUFFER_SIZE)
        #        print('data=%s', (data))
        #        if not data:
        #            f.close()
        #            print('file close()')
        #            break
                # write data to a file
        #        f.write(data)
        #    while True:
                # print('receiving data...')
        #        dataMD5 = s.recv(BUFFER_SIZE)
        #        print('MD5=%s', (dataMD5))
        #        if not dataMD5:
        #            print('code MD5')
         #           break
        print('Successfully get the file')
        s.close()
        print('connection closed')


for i in range(1):
    ClientThread(i).start()
