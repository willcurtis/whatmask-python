# Whatmask (Python Version)

A fast, lightweight tool for analyzing IP subnet masks, ranges, and ownership information.  
This version uses only native Python and the system `whois` command — no extra modules required.

## Features

- Accepts:
  - CIDR format (e.g., `/24`)
  - Dotted netmask (e.g., `255.255.255.0`)
  - Hexadecimal netmask (e.g., `0xffffff00`)
  - Wildcard mask (e.g., `0.0.0.255`)
  - Full IP/mask combinations (e.g., `192.168.1.10/24`)
- Outputs:
  - CIDR notation
  - Dotted decimal netmask
  - Hexadecimal netmask
  - Wildcard mask
  - Number of usable IP addresses
  - Network address and broadcast address
  - First and last usable IPs
- Colorized warnings for unusual subnets (`/31`, `/32`)
- WHOIS lookup using system `whois` to find:
  - Organization
  - Country
- **Brief mode** for compact one-line output
- Smart error handling:
  - Detects if user inputs an IP instead of a netmask
  - Clean guidance if mistakes are made

## Installation

1. Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/whatmask-python.git
cd whatmask-python
chmod +x getmask.py
```

2. (Optional) Install globally:

```bash
sudo cp getmask.py /usr/local/bin/whatmask
```

Now you can run `whatmask` from anywhere.

## Dependencies

- **Python 3.6+**
- **System `whois` command**

If needed, install `whois`:

```bash
# Ubuntu/Debian
sudo apt install whois

# RedHat/CentOS
sudo yum install whois

# macOS (Homebrew)
brew install whois
```

## Usage

### Standard Mode

```bash
./getmask.py 255.255.255.0
./getmask.py /26
./getmask.py 192.168.1.10/24
```

### Brief Mode

Outputs a compact single line:

```bash
./getmask.py --brief 192.168.1.10/24
```

Example:

```text
CIDR: /24 | Network: 192.168.1.0 | Broadcast: 192.168.1.255 | Range: 192.168.1.1-192.168.1.254
```

### WHOIS Lookup

Displays organization and country from the system's `whois` command:

```bash
./getmask.py --whois 8.8.8.8/24
```

## Warnings

- ⚠️ If you input a `/31` or `/32` network, a **colored warning** is displayed:
  - `/31`: Two-host subnet, point-to-point links
  - `/32`: Single IP (host route)

- ⚠️ If you accidentally input an IP address without a subnet mask,  
  you are advised to use the correct format:

Example:

```text
⚠️ Input 239.0.0.1 looks like an IP address, not a netmask.
⚠️ Hint: Use IP/mask format like 239.0.0.1/24
```

## License

MIT License — see [LICENSE](LICENSE) for full terms.
