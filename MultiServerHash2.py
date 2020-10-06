import socket
from threading import Thread
# Importa libreria hashlib para realizar verificacion de integridad con md5
import hashlib
import tqdm
import os


TCP_IP = ''
TCP_PORT = 65432
BUFFER_SIZE = 1024
HEADERSIZE = 10
SEPARATOR = "<SEPARATOR>"

# Variable que almacena el codigo md5 en hexadecimal del archivo a enviar
Verification_code = 'NoCodigo'

# Crea un codigo de verificacion MD5 por el archivo que se este pasando por parametro y lo escribe en un archivo .txt


def createVerificationCode(filename):
    global Verification_code
    if(Verification_code == 'NoCodigo'):
        file = open(filename, 'rb')
        Verification_code = hashlib.md5(file.read()).hexdigest()
        print(Verification_code)
        vf = open("MD5.txt", "w")
        vf.write(Verification_code)
        vf.close()
    return Verification_code


class ClientThread(Thread):

    def __init__(self, ip, port, sock):
        Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.sock = sock
        print(" New thread started for "+ip+":"+str(port))

    def run(self):
        filename = 'dogs.jpg'
        # get the file size
        filesize = os.path.getsize(filename)
        createVerificationCode(filename)
        self.sock.send(
            f"{filename}{SEPARATOR}{filesize}{SEPARATOR}{Verification_code}".encode())
        progress = tqdm.tqdm(range(
            filesize), f"Sending {filename}", unit="B", unit_scale=True, unit_divisor=1024)
        with open(filename, "rb") as f:
            for _ in progress:
                # read the bytes from the file
                bytes_read = f.read(BUFFER_SIZE)
                if not bytes_read:
                    # file transmitting is done
                    f.close()
                    # Recibe la comprobacion de hash del cliente
                    received = self.sock.recv(BUFFER_SIZE).decode()
                    filename, filesize = received.split(SEPARATOR)
                    print(filename)
                    print(filesize)
                    #compVerification = msgReceived.split(SEPARATOR)[0]
                    # print(compVerification)
                    break
                # we use sendall to assure transimission in
                # busy networks
                self.sock.sendall(bytes_read)
                # update the progress bar
                progress.update(len(bytes_read))
        # close the socket
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
