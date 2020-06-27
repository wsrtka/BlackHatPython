import sys
import socket
import getopt
import threading
import subprocess

listen = False
command = False
upload = False
execute = ''
target = ''
upload_destination = ''
port = 0


def usage():
    print('BHP Net tool')
    print('Usage: netcat.py -t target_host -p port')
    print('-l --listen              listens on [host]:[port] for incoming connections')
    print('-e --execute=file_to_run executes file when connection is received')
    print('-c --command             initializes command line')
    print('-u --upload=destination  on connection, sends file and saves it in [destination]')
    print('\nExample usage:')
    print('netcat.py -t 192.168.0.1 -p 5555 -l -c')
    print('netcat.py -t 192.168.0.1 -p 5555 -l -u=c:\\target.exe')
    print('netcat.py -t 192.169.0.1 -p 5555 -l -e="cat /etc/passwd"')
    print('echo "ABCDEF" | ./netcat.py -t 192.168.11.12 -p 135')
    sys.exit(0)


def main():

    def client_sender(buffer):
        
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            client.connect((target, port))

            if len(buffer):
                client.send(buffer)

            while True:

                recv_len = 1
                response = ''

                while recv_len:

                    data = client.recv(4096).decode()
                    recv_len = len(data)
                    response += data

                    if recv_len < 4096:
                        break

                print(response)

                buffer = input('')
                buffer += '\n'

                client.send(buffer)

        except:
            print('[*] Error encountered, closing.')
            client.close()


    def server_loop():
        global target

        if not len(target):
            target = '0.0.0.0'

        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((target, port))
        server.listen(5)

        while True:
            client_socket, addr = server.accept()

            client_thread = threading.Thread(target=client_handler, args=(client_socket,))
            client_thread.start()


    global listen
    global command
    global upload
    global execute
    global target
    global upload_destination
    global port

    if not len(sys.argv[1:]):
        usage()

    try:
        opts, args = getopt.getopt(sys.argv[1:], 'hle:t:p:cu:', ['help', 'listen', 'execute', 'target', 'port', 'command', 'upload'])
    except getopt.GetoptError as err:
        print(str(err))
        usage()

    for o, a in opts:
        if o in ('-h', '--help'):
            usage()
        elif o in ('-l', '--listen'):
            listen = True
        elif o in ('-e', '--execute'):
            execute = a
        elif o in ('-c', '--command'):
            command = True
        elif o in ('-u', '--upload'):
            upload_destination = a
        elif o in ('-t', '--target'):
            target = a
        elif o in ('-p', '--port'):
            port = int(a)
        else:
            assert False, "Unhandled option"

    if not listen and len(target) and port > 0:
        buffer = sys.stdin.read()
        client_sender(buffer)

    if listen:
        server_loop()


main()