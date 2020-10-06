import socket
import time
from threading import Thread
import tqdm
import os
import hashlib
import sys
TCP_IP = '34.71.37.77'
TCP_PORT = 65432
BUFFER_SIZE = 1024
SEPARATOR = "<SEPARATOR>"


def VerficateHash(originalHash, filename):
    file = open(filename, 'rb')
    md5_returned = hashlib.md5(file.read()).hexdigest()
    if originalHash == md5_returned:
        return "SI"
    else:
        return "NOUP"


class ClientThread(Thread):
    def __init__(self, id):
        Thread.__init__(self)
        print(" New thread started at "+str(time.time())+":"+str(TCP_PORT))
        self.id = id

    def run(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((TCP_IP, TCP_PORT))
        received = s.recv(BUFFER_SIZE).decode()
        filename, filesize, mHash = received.split(SEPARATOR)
        # remove absolute path if there is
        filename = os.path.basename(filename)
        filename = filename.split('.')[0] + \
            str(self.id) + str(time.time()).split('.')[0] + '.jpg'
        # convert to integer
        filesize = int(filesize)
        progress = tqdm.tqdm(range(
            filesize), f"Receiving {filename}", unit="B", unit_scale=True, unit_divisor=1024)
        with open(filename, "wb") as f:
            for _ in progress:
                # read 1024 bytes from the socket (receive)
                bytes_read = s.recv(BUFFER_SIZE)
                if not bytes_read:
                    # cierra el archivo
                    f.close()
                    # Verificar integridad del mensaje
                    resVerification = VerficateHash(mHash, filename)
                    print('\n'+resVerification)
                    # Informar al servidor si el resultado verificacion
                    strSize = sys.getsizeof(resVerification)
                    # print(strSize)
                    # s.send(f"{resVerification}{SEPARATOR}{strSize}".encode())
                    # file transmitting is done
                    break
                else:
                    # write to the file the bytes we just received
                    f.write(bytes_read)
                    # update the progress bar
                    progress.update(len(bytes_read))

        print('Obtuvo exitosamente el archivo')
        s.close()
        print('Conexion cerrrada')


for i in range(1):
    ClientThread(i).start()
