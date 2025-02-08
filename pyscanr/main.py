import sys
import subprocess
import ipaddress

class Colors:
    RED: str = "\x1b[0;31m"
    GREEN: str = "\x1b[0;32m"
    RESET: str = "\x1b[0m"

def scan_subnet() -> None:
    """
    Begins the program.
    Reads the first arg and attempts to ping the given subnet
    """
    if len(sys.argv) < 2:
        print("No subnet to scan. Exiting...")
        sys.exit(1)

    arg: list[str] = sys.argv[1].split("/")
    if len(arg) != 2:
        print(f"{Colors.RED}{sys.argv[1]}{Colors.RESET} is not a valid subnet!")
        sys.exit(1)

    ok: bool = True
    subnet_id = arg[0]
    netmask_length = arg[1]

    octets: list[str] = subnet_id.split(".")
    if len(octets) != 4:
        ok = False
    try:
        for octet in octets:
            if not (0 <= int(octet) and int(octet) <= 255):
                raise ValueError()
    except ValueError: 
        ok = False

    try:
        if not (1 <= int(netmask_length) and int(netmask_length) <= 32):
            raise ValueError()
    except ValueError:
        ok = False

    if not ok:
        print(f"{Colors.RED}{sys.argv[1]}{Colors.RESET} is not a valid subnet!")
        sys.exit(1)

    processes: dict[str, subprocess.Popen] = {}
    try:
        subnet = ipaddress.IPv4Network(sys.argv[1])
    except ValueError:
        print(f"{Colors.RED}{sys.argv[1]}{Colors.RESET} has host bits set!")
        exit(1)

    print(f"Scanning {sys.argv[1]}. Please wait...")
    for host in subnet.hosts():
        processes[str(host)] = subprocess.Popen(["ping", "-n" if sys.platform.lower() == "win32" else "-c", "1", str(host)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    alive: list[str] = []
    while processes:
        for ip, process in processes.items():
            if process.poll() is not None:
                if process.returncode == 0:
                    alive.append(ip)
                del processes[ip]
                break
    insertion_sort(alive)

    for online in alive:
        print(f"{Colors.GREEN}{online}{Colors.RESET}: ICMP echo response received")


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

if __name__ == "__name__":
    scan_subnet()
