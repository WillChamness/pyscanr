import argparse
from pyscanr import scan_subnet_user, scan_subnet
from socket import gethostbyname, gethostname

def _init() -> None:
    parser = argparse.ArgumentParser(add_help=False, description="Pings a range of IP addresses")

    parser.add_argument("subnet", type=str, help="a.b.c.d/xy")
    parser.add_argument("-h", "--help", action="help", default=argparse.SUPPRESS, help="Show this help message and exit.")
    parser.add_argument("-s", "--source", required=False, type=str, help="The source address to ping from. If not specified, a best effort will be made to decide the source address.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Show information in real time")
    parser.add_argument("-a", "--all-hosts", action="store_true", help="Print all hosts, including unreachable ones")
    parser.add_argument("-u", "--user", action="store_true", help="Run in user mode if using Linux. Generally significantly faster, but may spike CPU usage. Not recommended for medium- to large-sized networks.")

    args = parser.parse_args()

    src_ip = args.source if args.source is not None else gethostbyname(gethostname())
    dst_subnet = args.subnet

    if args.user:
        scan_subnet_user(src_ip, dst_subnet, print_all=args.all_hosts, verbose=args.verbose)
    else:
        scan_subnet(src_ip, dst_subnet, print_all=args.all_hosts, verbose=args.verbose)


if __name__ == "__main__":
    _init()
