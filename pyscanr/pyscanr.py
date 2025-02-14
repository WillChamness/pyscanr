import sys
import logging
import subprocess
import ipaddress
import socket
from threading import Thread
from scapy.all import IP, ICMP, sr1
from typing import Iterator

class Colors:
    RED: str = "\x1b[0;31m"
    GREEN: str = "\x1b[0;32m"
    RESET: str = "\x1b[0m"

class IcmpTypes:
    ECHO_REPLY = 0
    DESTINATION_UNREACHABLE = 1
    ECHO_REQUEST = 8

class IcmpDestUnreachableCodes:
    NETWORK_UNREACHABLE = 0
    HOST_UNREACHABLE = 1
    DESTINATION_NETWORK_UNKNOWN = 6
    DESTINATION_HOST_UNKNOWN = 7


class PingWorkerThread(Thread):
    def __init__(self, src: str, dst: ipaddress.IPv4Network|ipaddress.IPv4Address, verbose: bool, include_network_address: bool=False, include_broadcast: bool=False) -> None:
        super().__init__()
        self._src = src
        self._dst = dst
        self._verbose = verbose
        self. _include_network_addr = include_network_address
        self. _include_broadcast = include_broadcast
        self._results: dict[str, bool] = {}

    def run(self) -> None:
        dst: str
        if isinstance(self._dst, ipaddress.IPv4Network):
            for host in self._dst.hosts(): 
                dst = str(host)
                self._results[dst] = ping_host(self._src, dst)
                if self._verbose:
                    print(dst)

            if self._include_network_addr:
                dst = str(self._dst.network_address)
                self._results[dst] = ping_host(self._src, dst)
                if self._verbose:
                    print(dst)

            if self._include_broadcast:
                dst = str(self._dst.broadcast_address)
                self._results[dst] = ping_host(self._src, dst)
                if self._verbose:
                    print(dst)
        else:
            dst = str(self._dst)
            self._results[dst] = ping_host(self._src, dst)
        

    def results(self) -> dict[str, bool]:
        if self.is_alive():
            raise RuntimeError("Thread is not finished!")
        else:
            return self._results


def validate_ip(addr: str) -> bool:
    octets: list[str] = addr.split(".")
    if len(octets) != 4:
        return False

    oct1, oct2, oct3, oct4 = octets[0], octets[1], octets[2], octets[3]

    try:
        if str(int(oct1)) != oct1 or str(int(oct2)) != oct2 or str(int(oct3)) != oct3 or str(int(oct4)) != oct4: # check for leading 0s
            return False
    except ValueError:
        return False

    ip: int = (2**24 * int(oct1)) + (2**16 * int(oct2)) + (2**8 * int(oct3)) + int(oct4)

    # validate that the address is a valid 32-bit integer
    return 0 <= ip and ip < 2**32



def validate_subnet(subnet: str) -> bool:
    subnet_range: list[str] = subnet.split("/")
    if len(subnet_range) != 2:
        return False

    subnet_id: str = subnet_range[0]
    netmask_length: str = subnet_range[1]

    try:
        if str(int(netmask_length)) != netmask_length: # check for valid integer formatting and leading 0s
            return False
    except ValueError:
        return False

    return validate_ip(subnet_id) and 1 <= int(netmask_length) and int(netmask_length) <= 32


def ping_host(src: str, dst: str) -> bool:
    ICMP_ECHO_REQUEST_DEFAULT_CODE = 0

    icmp = ICMP(type=IcmpTypes.ECHO_REQUEST, code=ICMP_ECHO_REQUEST_DEFAULT_CODE)
    ip = IP(src=src, dst=dst)

    response = sr1(ip / icmp, verbose=0, timeout=0.1, retry=1)
    if response:
        return response["ICMP"].type == IcmpTypes.ECHO_REPLY
    else:
        return False


def scan_subnet(src: str, dst_subnet: str, print_all: bool=False, verbose: bool=False) -> None:
    if not verbose:
        logging.getLogger("scapy.runtime").setLevel(logging.ERROR)
    if not validate_ip(src):
        print(f"{Colors.RED}{src}{Colors.RESET} is not a valid IP address!")
        return
    if not validate_subnet(dst_subnet):
        print(f"{Colors.RED}{dst_subnet}{Colors.RESET} is not a valid subnet!")
        return
    try:
        subnet = ipaddress.IPv4Network(dst_subnet)
    except ValueError:
        print(f"{Colors.RED}{dst_subnet}{Colors.RESET} has host bits set!")
        return

    print(f"Scanning {dst_subnet} from {src}. Please wait...")

    NETMASK_LENGTH_DIFFERENCE: int = 4
    NUM_THREADS: int = 2 ** NETMASK_LENGTH_DIFFERENCE 

    threads: list[PingWorkerThread] = []
    subnets: Iterator[ipaddress.IPv4Network] = subnet.subnets(prefixlen_diff=NETMASK_LENGTH_DIFFERENCE)

    for i in range(NUM_THREADS):
        thread: PingWorkerThread
        # check if NUM_THREADS == 1 for possible future functionality
        if subnet.netmask == ipaddress.IPv4Network("0.0.0.0/" + str(32 - NETMASK_LENGTH_DIFFERENCE)).netmask: # netmask length + NETMASK_LENGTH_DIFFERENCE == 32 in this case. every thread pings only one host. NUM_THREADS is an upper bound
            if i != 0 and i != NUM_THREADS - 1:
                thread = PingWorkerThread(src, next(subnets), verbose)
        elif i == 0 and NUM_THREADS != 1:
            thread = PingWorkerThread(src, next(subnets), verbose, include_broadcast=True)
        elif i == NUM_THREADS - 1 and NUM_THREADS != 1:
            thread = PingWorkerThread(src, next(subnets), verbose, include_network_address=True)
        else:
            thread = PingWorkerThread(src, next(subnets), verbose, include_network_address=True, include_broadcast=True)

        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    results: dict[str, bool] = {}
    for thread in threads:
        for ip, status in thread.results().items():
            results[ip] = status

    for host in subnet.hosts():
        ip_addr: str = str(host)
        if results[ip_addr]:
            print(f"{Colors.GREEN}{ip_addr}{Colors.RESET}: ICMP echo reply received")
        elif print_all:
            print(f"{Colors.RED}{ip_addr}{Colors.RESET}: ICMP echo reply not received")
    

def scan_subnet_user(src: str, dst_subnet: str, print_all: bool=False, verbose: bool=False) -> None:
    """
    Scans the subnet by spawning a number of ping processes at the same time
    """
    if not validate_subnet(dst_subnet):
        print(f"{Colors.RED}{dst_subnet}{Colors.RESET} is not a valid subnet!")
        return

    processes: dict[str, subprocess.Popen] = {}
    try:
        subnet = ipaddress.IPv4Network(dst_subnet)
    except ValueError:
        print(f"{Colors.RED}{dst_subnet}{Colors.RESET} has host bits set!")
        return

    print(f"Scanning {dst_subnet}. Please wait...")
    for host in subnet.hosts():
        processes[str(host)] = subprocess.Popen(["ping", "-n" if sys.platform.lower() == "win32" else "-c", "1", str(host)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    alive: list[str] = []
    dead: list[str] = []
    while processes:
        for ip, process in processes.items():
            if process.poll() is not None:
                if process.returncode == 0:
                    alive.append(ip)
                elif print_all:
                    dead.append(ip)
                del processes[ip]
                if verbose:
                    print(ip)
                break

    if not print_all:
        insertion_sort(alive)
        for online in alive:
            print(f"{Colors.GREEN}{online}{Colors.RESET}: ICMP echo reply received")
    else:
        hosts: list[str] = [*alive, *dead]
        insertion_sort(hosts)
        for ip in hosts:
            if ip in alive:
                print(f"{Colors.GREEN}{ip}{Colors.RESET}: ICMP echo reply received")
            else:
                print(f"{Colors.RED}{ip}{Colors.RESET}: ICMP echo reply not received")




def insertion_sort(ip_addresses: list[str]) -> None:
    def swap(i, j, lst):
        tmp = lst[i]
        lst[i] = lst[j]
        lst[j] = tmp

    for i in range(1, len(ip_addresses)):
        for j in range(i, 0, -1):
            octets: list[tuple[int, int]] = [(int(octet1), int(octet2)) for octet1, octet2 in zip(ip_addresses[j-1].split("."), ip_addresses[j].split("."))]
            if octets[0][0] > octets[0][1]:
                swap(j, j-1, ip_addresses)
            elif octets[0][0] == octets[0][1] and octets[1][0] > octets[1][1]:
                swap(j, j-1, ip_addresses)
            elif octets[0][0] == octets[0][1] and octets[1][0] == octets[1][1] and octets[2][0] > octets[2][1]:
                swap(j, j-1, ip_addresses)
            elif octets[0][0] == octets[0][1] and octets[1][0] == octets[1][1] and octets[2][0] == octets[2][1] and octets[3][0] > octets[3][1]:
                swap(j, j-1, ip_addresses)
            else:
                break

