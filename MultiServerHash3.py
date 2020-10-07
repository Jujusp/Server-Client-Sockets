import socket
from threading import Thread
import struct
import hashlib
import time
import sys
import datetime
TCP_IP = ''
TCP_PORT = 65432
BUFFER_SIZE = 1024
END_TRANSMISION = b'TERMINO'

# Variable que almacena el codigo md5 en hexadecimal del archivo a enviar
Verification_code = 'NoCodigo'
# Variables usadas por el log
fileGlobal = ""


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
        print(" Nuevo Thread comenzado por"+ip+":"+str(port))

    def run(self):
        tInicio = 0
        tFinal = 0
        numPaquetesEnviados = 0
        numPaquetesRecibidos = 0
        bytesEnviados = 0
        bytesRecibidos = 0
        fileGlobal = 0
        correctoGlobal = True

        filename = fileGlobal
        print(filename)
        f = open(filename, 'rb')

        while True:
            l = f.read(BUFFER_SIZE)
            while (l):
                numPaquetesEnviados += 1
                bytesEnviados += sys.getsizeof(l)
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
        rta = recv_one_message(self.sock).decode()
        print(rta)
        correctoGlobal &= rta == 'HASH VERIFICADO'
        numPaquetesCliente, numBytesCliente = recv_one_message(
            self.sock).decode().split(';')
        print("num"+numPaquetesCliente)
        numPaquetesRecibidos += numPaquetesCliente
        print("by"+numBytesCliente)
        bytesRecibidos += numBytesCliente
        self.sock.close()
        with open(LogTxt, 'w') as log:
            tFinal = time.time_ns()
            log.write("Tiempo final de ejecucion: " + str(tFinal) + '\n')
            log.write("Tiempo de ejecucion: " + str((tFinal-tInicio)) + '\n')
            log.write("Numero de paquetes enviados: " +
                      str(numPaquetesEnviados) + "\n")
            log.write("Numero de paquetes recibidos: " +
                      str(numPaquetesRecibidos) + "\n")
            log.write("Numero de bytes enviados: " + str(bytesEnviados) + "\n")
            log.write("Numero de bytes recibidos: " +
                      str(bytesRecibidos) + "\n")
            log.write("Correctitud del envio: " + str(correctoGlobal) + "\n")
            log.close()


tcpsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcpsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
tcpsock.bind((TCP_IP, TCP_PORT))
threads = []
# Aplicacion
print("Hola!, bienvenido a la aplicacion del grupo 11, por favor selecciona el archivo de video a mandar: "+"\n")
print("1. Video 1 de  100 MB"+"\n")
print("2. Video 2 de  250 MB"+"\n")
opcion = int(input("Ingresa una opción: "))
fileGlobal = 'ventilador_100.mp4' if (opcion == 1) else 'hielo_250.mp4'
print("Listo, menciona el numero de clientes a los que quieres antender en simultaneo para enviar el archivo: "+"\n")
opcion2 = int(input("Ingresa el numero de clientes: "))
# Preparacion del log
LogTxt = 'log_servidor' + \
    '_'+str(time.time()).split('.')[0] + '.txt'

with open(LogTxt, 'w') as log:
    log.write("Fecha y hora de la prueba: " +
              str(datetime.datetime.now()) + '\n')
    log.close()
while True:
    tcpsock.listen(25)
    print("Esperando por conexiones entrantes...")
    (conn, (ip, port)) = tcpsock.accept()
    print('Conexion desde  ', (ip, port))
    newthread = ClientThread(ip, port, conn)
    threads.append(newthread)
    while len(threads) >= opcion2:
        for t in threads:
            threads[t].start()
        for t in threads:
            threads[t].join()
            threads.remove(t)
