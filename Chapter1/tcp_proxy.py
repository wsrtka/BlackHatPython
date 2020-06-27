import sys
import socket
import threading


def server_loop(local_host, local_port, remote_host, remote_port, receive_first):

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        server.bind((local_host, local_port))
    except:
        print('[!] Unsuccessful attempt of listening on port %s:%d' % (local_host, local_port))
        print('[!] Find another socket or get adequate access rights.')
        sys.exit(0)
    
    print('[*] Listening on port %s:%d' % (local_host, local_port))

    server.listen(5)

    while True:
        
        client_socket, addr = server.accept()

        print('[=>] Received incoming connection from %s:%d' % (addr[0], addr[1]))

        proxy_thread = threading.Thread(target=proxy_handler, args=(client_socket, remote_host, remote_port, receive_first))
        proxy_thread.start()


def main():

    if len(sys.argv[1:]) != 5:
        
        print('Usage: python3 ./tcp_proxy.py [localhost] [localport] [remotehost] [remoteport] [receive_first]')
        print('Example: python3 ./tcp+proxy 127.0.0.1 9000 10.12.132.1 9000 True')
        sys.exit(0)

    local_host = sys.argv[1]
    local_port = int(sys.argv[2])

    remote_host = sys.argv[3]
    remote_port = int(sys.argv[4])

    receive_first = True if 'True' in sys.argv[5] else False

    server_loop(local_host, local_port, remote_host, remote_port, receive_first)

if __name__ == '__main__':
    main()