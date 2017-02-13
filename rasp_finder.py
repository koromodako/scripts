#!/usr/bin/env python3
# -!- encoding:utf8 -!-

from subprocess import check_output

IPV=4
TARGET_WIFI_HWADDR='74:da:38:0a:33:60'
TARGET_INET_HWADDR='b8:27:eb:60:cf:c9'

def run_cmd(args):
    print('run: %s' % ' '.join(args))
    return check_output(args).decode('utf-8')

def find_base_addr():
    base_addr = None
    if_config = run_cmd(['ifconfig'])
    for l in if_config.split('\n'):
        if 'inet' in l:
            base_addr = l.strip().split(' ')[1]
            break
    base_addr_bytes = base_addr.split('.')
    base_addr_bytes[3]='0'
    return '.'.join(base_addr_bytes)

def nmap_discover(base_addr, mask='/24'):
    run_cmd(['nmap', '-nsP', base_addr+mask])

def get_rasp_ip(arp_config, mac_addr):
    ip = None
    for l in arp_config.split('\n'):
        if mac_addr in l:
            ip = l.split(' ')[0]
            break
    return ip

def print_rasp_ip(ip):
    print("""
Your raspberry-pi have the following IP : %s
You can open a SSH connection using the following command :
> ssh -l pi %s
""" % (ip,ip))


# FUNCTIONS ----------------------------------------------------------

# TEST PARAMS VALIDITY
print("Searching for a raspberry-pi on your L.A.N. ...please wait...")
print("Starting Nmap for a quick network recon...")

base_addr = find_base_addr()

if base_addr is None:
    print('Failed to retrieve base address.')
    exit(1)

print('base address is : %s' % base_addr)
nmap_discover(base_addr, '/24')
arp_config = run_cmd(['arp', '-n'])

print("Searching for raspberry-pi wifi hardware address...")

ip = get_rasp_ip(arp_config, TARGET_WIFI_HWADDR)
if ip is None:
    print('No device found on wifi interface.')
else:
    print_rasp_ip(ip)
    exit(0)

print("Searching for raspberry-pi inet hardware address...")

ip = get_rasp_ip(arp_config, TARGET_INET_HWADDR)
if ip is None:
    print('No device found on inet interface.')
else:
    print_rasp_ip(ip)
    exit(0)

print("No raspberry-pi found on this network !")
exit(2)
