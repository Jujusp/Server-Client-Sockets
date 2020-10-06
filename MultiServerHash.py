import socket
from threading import Thread
# Importa libreria hashlib para realizar verificacion de integridad con md5
import hashlib

TCP_IP = ''
TCP_PORT = 65432
BUFFER_SIZE = 1024
# Variable que almacena el codigo md5 en hexadecimal del archivo a enviar
Verification_code = 'NoCodigo'

# Crea un codigo de verificacion MD5 por el archivo que se este pasando por parametro y lo escribe en un


def createVerificationCode(filename, Vcode):
    if(Vcode == 'NoCodigo'):
        file = open(filename, 'rb')
        Vcode = hashlib.md5(file.read()).hexdigest()
        print(Vcode)
        vf = open("MD5.txt", "a")
        vf.write(Vcode)
        vf.close()
    return Vcode


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
                self.sock.send(l)
                l = f.read(BUFFER_SIZE)
            if not l:
                f.close()
                self.sock.close()
                break
        Verification_code = createVerificationCode(filename, Verification_code)


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
