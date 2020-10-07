import socket
import time
from threading import Thread
import struct
import hashlib
import datetime
import sys

TCP_IP = '34.71.37.77'
TCP_PORT = 65432
BUFFER_SIZE = 1024
END_TRANSMISION = b'TERMINO'


def VerificateHash(originalHash, filename):
    file = open(filename, 'rb')
    md5_returned = hashlib.md5(file.read()).hexdigest()
    if originalHash.decode() == md5_returned:
        return "HASH VERIFICADO"
    else:
        return "HASH ALTERADO"


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
        print(" Nuevo thread en"+str(time.time())+":"+str(TCP_PORT))
        self.id = id

    def run(self):
        # Preparacion del log
        LogTxt = 'log_cliente_' + \
            str(self.id) + '_'+str(time.time()).split('.')[0] + '.txt'
        # Variables usadas por el log
        tInicio = 0
        tFinal = 0
        numPaquetesRecibidos = 0
        bytesRecibidos = 0
        with open(LogTxt, 'w') as log:
            log.write("Fecha y hora de la prueba: " +
                      str(datetime.datetime.now()) + '\n')
            # Ejecucion del programa
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((TCP_IP, TCP_PORT))
            tInicio = time.time_ns()
            log.write("Tiempo de inicio de ejecucion de Th_" +
                      str(self.id)+" : "+str(tInicio)+'\n')
            recived_f = 'imgt_thread' + \
                str(self.id) + str(time.time()).split('.')[0] + '.jpg'

            with open(recived_f, 'wb') as f:
                print('Archivo abierto')
                while True:
                    data = recv_one_message(s)
                    # print('data=%s', (data))
                    if repr(data) == repr(END_TRANSMISION):
                        f.close()
                        print('file close()')
                        tFinal = time.time_ns()
                        log.write("Tiempo final de ejecucion de Th_"+str(self.id) + " : "
                                  + str(tFinal) + '\n')
                        log.write("Tiempo de ejecucion de Th_"+str(self.id)+" : "
                                  + str((tFinal-tInicio)) + '\n')
                        break
                    # write data to a file
                    f.write(data)
                    numPaquetesRecibidos += 1
                    bytesRecibidos += sys.getsizeof(data)

                log.write("Numero paquetes recibidos de Th_" +
                          str(self.id)+" : "+str(numPaquetesRecibidos) + '\n')
                log.write("Bytes recibidos por Th_" +
                          str(self.id)+" : "+str(bytesRecibidos) + '\n')
                codigoVerificacion = recv_one_message(s)
                rtaVerificacion = VerificateHash(codigoVerificacion, recived_f)
                print('Resultado de validacion: ' + rtaVerificacion)
                send_one_message(s, rtaVerificacion.encode())
                send_one_message(
                    s, str(numPaquetesRecibidos+";"+bytesRecibidos).encode())
            print('Archivo descargado con exito')
            s.close()
            print('Conexion cerrada')


for i in range(1):
    ClientThread(i).start()
