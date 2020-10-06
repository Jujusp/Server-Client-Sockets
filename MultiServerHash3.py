import socket
from threading import Thread
import struct
import hashlib
TCP_IP = ''
TCP_PORT = 65432
BUFFER_SIZE = 1024
END_TRANSMISION = b'TERMINO'

# Variable que almacena el codigo md5 en hexadecimal del archivo a enviar
Verification_code = 'NoCodigo'


def createVerificationCode(filename):
    global Verification_code
    if(Verification_code == 'NoCodigo'):
        file = open(filename, 'rb')
        Verification_code = hashlib.md5(file.read()).hexdigest()
        print("Codigo de verificacion:"+Verification_code)
    return Verification_code


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

    def __init__(self, ip, port, sock):
        Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.sock = sock
        print(" New thread started for "+ip+":"+str(port))

    def run(self):
        filename = 'dogs.jpg'
        f = open(filename, 'rb')
        while True:
            l = f.read(BUFFER_SIZE)
            while (l):
                send_one_message(self.sock, l)
                l = f.read(BUFFER_SIZE)
            if not l:
                f.close()
                print('Termino la transferencia')
                break
        print('Enviando Comando:', repr(END_TRANSMISION))
        send_one_message(self.sock, END_TRANSMISION)
        # Envia codigo de verificacion
        send_one_message(self.sock, createVerificationCode(filename).encode())
        # Recibe respuesta del cliente
        print(self.sock)
        rta = recv_one_message(self.sock)
        print(rta.decode())

        self.sock.close()


tcpsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcpsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
tcpsock.bind((TCP_IP, TCP_PORT))
threads = []

while True:
    tcpsock.listen(25)
    print("Waiting for incoming connections...")
    (conn, (ip, port)) = tcpsock.accept()
    print('Got connection from ', (ip, port))
    newthread = ClientThread(ip, port, conn)
    newthread.start()
    threads.append(newthread)

for t in threads:
    t.join()
