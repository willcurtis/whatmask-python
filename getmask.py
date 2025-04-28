#!/usr/bin/env python3
import ipaddress
import sys
import subprocess
import shutil
import re

# ANSI color codes
RESET = "\033[0m"
BOLD = "\033[1m"
HEADER = "\033[94m"
WARNING = "\033[93m"

# Unicode symbol
WARN_SYMBOL = "\u26A0\uFE0F"

def parse_mask(mask_str, suppress_ip_warning=False):
    try:
        if mask_str.startswith("0x"):
            mask_int = int(mask_str, 16)
            mask = ipaddress.IPv4Address(mask_int)
            return str(mask)
        elif any(c.isalpha() for c in mask_str):
            raise ValueError
        else:
            parts = mask_str.split(".")
            if len(parts) == 4:
                try:
                    ipaddress.IPv4Address(mask_str)
                    if not suppress_ip_warning:
                        print(f"{WARNING}Input {mask_str} looks like an IP address, not a netmask.{RESET}")
                        print(f"{WARNING}Hint: Use IP/mask format like {mask_str}/24{RESET}")
                        sys.exit(1)
                    else:
                        return mask_str
                except ipaddress.AddressValueError:
                    pass
                if any(int(p) > 255 for p in parts):
                    raise ValueError
                return mask_str
            elif len(parts) == 1 and parts[0].isdigit():
                cidr = int(parts[0])
                if not (0 <= cidr <= 32):
                    raise ValueError
                return str(ipaddress.IPv4Network(f"0.0.0.0/{cidr}").netmask)
            else:
                raise ValueError
    except Exception:
        print("Invalid mask format.")
        sys.exit(1)

def warn_about_weird_subnet(cidr):
    if cidr == 31:
        print(f"{WARNING}{WARN_SYMBOL} Warning: /31 subnet — only 2 IPs (point-to-point link){RESET}")
    elif cidr == 32:
        print(f"{WARNING}{WARN_SYMBOL} Warning: /32 subnet — single host address{RESET}")

def mask_to_info(mask_str):
    netmask = ipaddress.IPv4Address(mask_str)
    wildcard = ipaddress.IPv4Address(0xFFFFFFFF ^ int(netmask))
    cidr = ipaddress.IPv4Network(f"0.0.0.0/{mask_str}").prefixlen
    usable = (2 ** (32 - cidr)) - 2 if cidr < 31 else (2 ** (32 - cidr))

    print(f"{HEADER}------------------------------------------------{RESET}")
    print(f"{BOLD}      TCP/IP SUBNET MASK EQUIVALENTS{RESET}")
    print(f"{HEADER}------------------------------------------------{RESET}")
    print(f"{'CIDR':25}: /{cidr}")
    print(f"{'Netmask':25}: {netmask}")
    print(f"{'Netmask (hex)':25}: {hex(int(netmask))}")
    print(f"{'Wildcard Bits':25}: {wildcard}")
    print(f"{'Usable IP Addresses':25}: {usable:,}")
    warn_about_weird_subnet(cidr)

def system_whois_lookup(ip_str):
    if shutil.which("whois") is None:
        print(f"{WARNING}System 'whois' command not found. Install with 'apt install whois' or 'brew install whois'.{RESET}")
        return
    try:
        result = subprocess.run(["whois", ip_str], capture_output=True, text=True, timeout=10)
        text = result.stdout

        org_patterns = [
            r'OrgName:\s*(.*)',
            r'organisation:\s*(.*)',
            r'Org-name:\s*(.*)',
            r'descr:\s*(.*)',
            r'netname:\s*(.*)'
        ]

        country_pattern = r'Country:\s*(.*)'

        org = None
        for pattern in org_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                org = match.group(1).strip()
                break

        country = re.search(country_pattern, text, re.IGNORECASE)

        print(f"{HEADER}------------------------------------------------{RESET}")
        print(f"{BOLD}              WHOIS INFORMATION{RESET}")
        print(f"{HEADER}------------------------------------------------{RESET}")
        print(f"{'Organization':25}: {org if org else 'N/A'}")
        print(f"{'Country':25}: {country.group(1).strip() if country else 'N/A'}")
    except Exception as e:
        print(f"{WARNING}System WHOIS lookup failed: {e}{RESET}")

def network_info(ip_str, mask_str, brief=False, do_whois=False):
    mask = parse_mask(mask_str, suppress_ip_warning=True)
    network = ipaddress.IPv4Network(f"{ip_str}/{mask}", strict=False)

    netmask = network.netmask
    wildcard = ipaddress.IPv4Address(0xFFFFFFFF ^ int(netmask))
    cidr = network.prefixlen
    usable = (2 ** (32 - cidr)) - 2 if cidr < 31 else (2 ** (32 - cidr))
    hosts = list(network.hosts())

    if brief:
        first = hosts[0] if usable >= 2 else network.network_address
        last = hosts[-1] if usable >= 2 else network.broadcast_address
        print(f"CIDR: /{cidr} | Network: {network.network_address} | Broadcast: {network.broadcast_address} | Range: {first}-{last}")
        return

    print(f"{HEADER}------------------------------------------------{RESET}")
    print(f"{BOLD}          TCP/IP NETWORK INFORMATION{RESET}")
    print(f"{HEADER}------------------------------------------------{RESET}")
    print(f"{'IP Entered':25}: {ip_str}")
    print(f"{'CIDR':25}: /{cidr}")
    print(f"{'Netmask':25}: {netmask}")
    print(f"{'Netmask (hex)':25}: {hex(int(netmask))}")
    print(f"{'Wildcard Bits':25}: {wildcard}")
    print(f"{HEADER}------------------------------------------------{RESET}")
    print(f"{'Network Address':25}: {network.network_address}")
    print(f"{'Broadcast Address':25}: {network.broadcast_address}")
    print(f"{'Usable IP Addresses':25}: {usable:,}")
    if usable >= 2:
        print(f"{'First Usable IP':25}: {hosts[0]}")
        print(f"{'Last Usable IP':25}: {hosts[-1]}")
    warn_about_weird_subnet(cidr)

    if do_whois:
        system_whois_lookup(ip_str)

def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} [--brief] [--whois] <mask|ip/mask> [netmask]")
        sys.exit(1)

    brief = False
    do_whois = False
    args = sys.argv[1:]

    if "--brief" in args:
        brief = True
        args.remove("--brief")

    if "--whois" in args:
        do_whois = True
        args.remove("--whois")

    if not args:
        print(f"Usage: {sys.argv[0]} [--brief] [--whois] <mask|ip/mask> [netmask]")
        sys.exit(1)

    if len(args) == 2:
        # Two arguments: IP + Netmask
        arg = f"{args[0]}/{args[1]}"
    else:
        arg = args[0]

    if '/' in arg:
        ip_part, mask_part = arg.split('/', 1)
        network_info(ip_part, mask_part, brief, do_whois)
    else:
        if brief or do_whois:
            print("Brief and WHOIS modes are only available for IP/mask inputs.")
            sys.exit(1)
        mask = parse_mask(arg)
        mask_to_info(mask)

if __name__ == "__main__":
    main()

