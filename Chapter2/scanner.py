import socket
import os
import struct
from ctypes import *
import threading
import time
from netaddr import IPAddress, IPNetwork


# host ip to listen on
host = '192.168.1.114'
# target subnet
subnet = '192.168.0.0/24'
# msg to check ICMP responses
magic_message = 'gottem'


def udp_sender(subnet, magic_message):

    time.sleep(5)

    sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    for ip in IPNetwork(subnet):
        try:
            sender.sendto(magic_message, ('%s' %ip, 65212))
        except Exception as e:
            print(str(e))       


class IP(Structure):

    # define the C ip struct using the ctypes library
    _fields_ = [
        ('ihl', c_ubyte, 4),
        ('version', c_ubyte, 4),
        ('tos', c_ubyte),
        ('len', c_ushort),
        ('id', c_ushort),
        ('offset', c_ushort),
        ('ttl', c_ubyte),
        ('protocol_num', c_ubyte),
        ('sum', c_ushort),
        ('src', c_uint32),
        ('dst', c_uint32),
    ]

    def __new__(self, socket_buffer=None):
        
        return self.from_buffer_copy(socket_buffer)

    def __init__(self, socket_buffer=None):

        # mapping protocol numbers to their names
        self.protocol_map = {1: 'ICMP', 6: 'TCP', 17: 'UDP'}

        # changing ip addresses from 32-bit packed format to dotted quad-string format
        self.src_address = socket.inet_ntoa(struct.pack('@I', self.src))
        self.dst_address = socket.inet_ntoa(struct.pack('@I', self.dst))

        try:
            self.protocol = self.protocol_map[self.protocol_num]
        except:
            self.protocol = str(self.protocol_num)


class ICMP(Structure):

    _fields_ = [
        ('type', c_ubyte),
        ('code', c_ubyte),
        ('checksum', c_ushort),
        ('unused', c_ushort),
        ('next_hop_mtu', c_ushort)
    ]

    def __new__(self, socket_buffer):
        
        return self.from_buffer_copy(socket_buffer)

    def __init__(self, socket_buffer):

        pass


if os.name == 'nt':
    socket_protocol = socket.IPPROTO_IP
else:
    socket_protocol = socket.IPPROTO_ICMP

sniffer = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket_protocol)
sniffer.bind((host, 0))
sniffer.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

# if on Windows, switch unlimited mode on
if os.name == 'nt':
    sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)

t = threading.Thread(target=udp_sender, args=(subnet, magic_message))
t.start()

try:
    while True:

        raw_buffer = sniffer.recvfrom(65565)[0]

        ip_header = IP(raw_buffer)

        print('Protocol: %s %s -> %s' % (ip_header.protocol, ip_header.src_address, ip_header.dst_address))

        if ip_header.protocol == 'ICMP':

            # find beginning of raw package with ICMP message
            offset = ip_header.ihl * 4
            buf = raw_buffer[offset:offset + sizeof(ICMP)]

            icmp_header = ICMP(buf)

            print('ICMP -> Type: %d Code: %d' % (icmp_header.type, icmp_header.code))

            if icmp_header.code == 3 and icmp_header.type == 3:
                if IPAddress(ip_header.src_address) in IPNetwork(subnet):
                    if raw_buffer[len(raw_buffer) - len(magic_message):] == magic_message:
                        print('Host: %s' % ip_header.src_address)
# end sniffer with ctrl+c
except KeyboardInterrupt:
    if os.name == 'nt':
        sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)