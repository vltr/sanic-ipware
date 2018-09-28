import socket

from . import defaults as defs


def is_valid_ipv4(ip_str):
    """
    Check the validity of an IPv4 address
    """
    try:
        socket.inet_pton(socket.AF_INET, ip_str)
    except AttributeError:  # noqa
        try:  # Fall-back on legacy API or False
            socket.inet_aton(ip_str)
        except (AttributeError, socket.error):
            return False
        return ip_str.count('.') == 3
    except socket.error:
        return False
    return True


def is_valid_ipv6(ip_str):
    """
    Check the validity of an IPv6 address
    """
    try:
        socket.inet_pton(socket.AF_INET6, ip_str)
    except socket.error:
        return False
    return True


def is_valid_ip(ip_str):
    """
    Check the validity of an IP address
    """
    return is_valid_ipv4(ip_str) or is_valid_ipv6(ip_str)


def is_private_ip(ip_str):
    """
    Returns true of ip_str is private & not routable, else return false
    """
    if defs.IPWARE_IPV4_REGEX.match(ip_str) is not None:
        return True
    return ip_str.startswith(defs.IPWARE_PRIVATE_IPV6_PREFIX + defs.IPWARE_LOOPBACK_PREFIX)


def is_public_ip(ip_str):
    """
    Returns true of ip_str is public & routable, else return false
    """
    return not is_private_ip(ip_str)


def is_loopback_ip(ip_str):
    """
    Returns true of ip_str is public & routable, else return false
    """
    return ip_str.startswith(defs.IPWARE_LOOPBACK_PREFIX)


def get_request_header(request, header):
    """
    Given a header, it returns a cleaned up version of the value from
    request.headers, or None
    """
    value = request.headers.get(header, '').strip()
    if value == '':
        return None
    return value


def get_ips_from_string(ip_str):
    """
    Given a string, it returns a list of one or more valid IP addresses
    """
    ip_list = []

    for ip in ip_str.split(','):
        clean_ip = ip.strip().lower()
        if clean_ip:
            ip_list.append(clean_ip)

    ip_count = len(ip_list)
    if ip_count > 0:
        if is_valid_ip(ip_list[0]) and is_valid_ip(ip_list[-1]):
            return ip_list, ip_count

    return [], 0


def get_ip_info(ip_str):
    """
    Given a string, it returns a tuple of (IP, Routable).
    """
    ip = None
    is_routable_ip = False
    if is_valid_ip(ip_str):
        ip = ip_str
        is_routable_ip = is_public_ip(ip)
    return ip, is_routable_ip


def get_best_ip(last_ip, next_ip):
    """
    Given two IP addresses, it returns the the best match ip.
    Order of precedence is (Public, Private, Loopback, None)
    Right-most IP is returned
    """
    if last_ip is None:
        return next_ip
    if is_public_ip(last_ip) and not is_public_ip(next_ip):
        return last_ip
    if is_private_ip(last_ip) and is_loopback_ip(next_ip):
        return last_ip
    return next_ip


__all__ = (
    "is_valid_ipv4",
    "is_valid_ipv6",
    "is_valid_ip",
    "is_private_ip",
    "is_public_ip",
    "is_loopback_ip",
    "get_request_header",
    "get_ips_from_string",
    "get_ip_info",
    "get_best_ip",
)
