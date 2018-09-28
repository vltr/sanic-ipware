import re

from .trie import Trie

# Search for the real IP address in the following order
# https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Forwarded-For
# X-Forwarded-For: <client>, <proxy1>, <proxy2>
# Configurable via settings.py
IPWARE_META_PRECEDENCE_ORDER = (
    "X-Forwarded-For",
    "X-Real-IP",
    "X-Client-IP",
    "X-Forwarded",
    "X-Cluster-Client-IP",
    "Forwarded-For",
    "Forwarded",
    "Via",
    # https://support.cloudflare.com/hc/en-us/articles/206776727-What-is-True-Client-IP-
    "True-Client-IP",
)

# Private IP addresses
# http://en.wikipedia.org/wiki/List_of_assigned_/8_IPv4_address_blocks
# https://en.wikipedia.org/wiki/Reserved_IP_addresses
# https://www.ietf.org/rfc/rfc1112.txt (IPv4 multicast)
# http://www.ietf.org/rfc/rfc3330.txt (IPv4)
# http://www.ietf.org/rfc/rfc5156.txt (IPv6)
# https://www.ietf.org/rfc/rfc6890.txt
# Regex would be ideal here, but this is keeping it simple
IPWARE_PRIVATE_IPV4_PREFIX = (
    "0.",  # messages to software
    "10.",  # class A private block
    "100.64.",  # carrier-grade NAT
    "100.65.",  # carrier-grade NAT
    "100.66.",  # carrier-grade NAT
    "100.67.",  # carrier-grade NAT
    "100.68.",  # carrier-grade NAT
    "100.69.",  # carrier-grade NAT
    "100.70.",  # carrier-grade NAT
    "100.71.",  # carrier-grade NAT
    "100.72.",  # carrier-grade NAT
    "100.73.",  # carrier-grade NAT
    "100.74.",  # carrier-grade NAT
    "100.75.",  # carrier-grade NAT
    "100.76.",  # carrier-grade NAT
    "100.77.",  # carrier-grade NAT
    "100.78.",  # carrier-grade NAT
    "100.79.",  # carrier-grade NAT
    "100.80.",  # carrier-grade NAT
    "100.81.",  # carrier-grade NAT
    "100.82.",  # carrier-grade NAT
    "100.83.",  # carrier-grade NAT
    "100.84.",  # carrier-grade NAT
    "100.85.",  # carrier-grade NAT
    "100.86.",  # carrier-grade NAT
    "100.87.",  # carrier-grade NAT
    "100.88.",  # carrier-grade NAT
    "100.89.",  # carrier-grade NAT
    "100.90.",  # carrier-grade NAT
    "100.91.",  # carrier-grade NAT
    "100.92.",  # carrier-grade NAT
    "100.93.",  # carrier-grade NAT
    "100.94.",  # carrier-grade NAT
    "100.95.",  # carrier-grade NAT
    "100.96.",  # carrier-grade NAT
    "100.97.",  # carrier-grade NAT
    "100.98.",  # carrier-grade NAT
    "100.99.",  # carrier-grade NAT
    "100.100.",  # carrier-grade NAT
    "100.101.",  # carrier-grade NAT
    "100.102.",  # carrier-grade NAT
    "100.103.",  # carrier-grade NAT
    "100.104.",  # carrier-grade NAT
    "100.105.",  # carrier-grade NAT
    "100.106.",  # carrier-grade NAT
    "100.107.",  # carrier-grade NAT
    "100.108.",  # carrier-grade NAT
    "100.109.",  # carrier-grade NAT
    "100.110.",  # carrier-grade NAT
    "100.111.",  # carrier-grade NAT
    "100.112.",  # carrier-grade NAT
    "100.113.",  # carrier-grade NAT
    "100.114.",  # carrier-grade NAT
    "100.115.",  # carrier-grade NAT
    "100.116.",  # carrier-grade NAT
    "100.117.",  # carrier-grade NAT
    "100.118.",  # carrier-grade NAT
    "100.119.",  # carrier-grade NAT
    "100.120.",  # carrier-grade NAT
    "100.121.",  # carrier-grade NAT
    "100.122.",  # carrier-grade NAT
    "100.123.",  # carrier-grade NAT
    "100.124.",  # carrier-grade NAT
    "100.125.",  # carrier-grade NAT
    "100.126.",  # carrier-grade NAT
    "100.127.",  # carrier-grade NAT
    "169.254.",  # link-local block
    "172.16.",  # class B private blocks
    "172.17.",  # class B private blocks
    "172.18.",  # class B private blocks
    "172.19.",  # class B private blocks
    "172.20.",  # class B private blocks
    "172.21.",  # class B private blocks
    "172.22.",  # class B private blocks
    "172.23.",  # class B private blocks
    "172.24.",  # class B private blocks
    "172.25.",  # class B private blocks
    "172.26.",  # class B private blocks
    "172.27.",  # class B private blocks
    "172.28.",  # class B private blocks
    "172.29.",  # class B private blocks
    "172.30.",  # class B private blocks
    "172.31.",  # class B private blocks
    "192.0.0.",  # reserved for IANA special purpose address registry
    "192.0.2.",  # reserved for documentation and example code
    "192.168.",  # class C private block
    "198.18.",  # reserved for inter-network communications between two separate subnets
    "198.19.",  # reserved for inter-network communications between two separate subnets
    "198.51.100.",  # reserved for documentation and example code
    "203.0.113.",  # reserved for documentation and example code
    "224.",  # multicast
    "225.",  # multicast
    "226.",  # multicast
    "227.",  # multicast
    "228.",  # multicast
    "229.",  # multicast
    "230.",  # multicast
    "231.",  # multicast
    "232.",  # multicast
    "233.",  # multicast
    "234.",  # multicast
    "235.",  # multicast
    "236.",  # multicast
    "237.",  # multicast
    "238.",  # multicast
    "239.",  # multicast
    "240.",  # reserved
    "241.",  # reserved
    "242.",  # reserved
    "243.",  # reserved
    "244.",  # reserved
    "245.",  # reserved
    "246.",  # reserved
    "247.",  # reserved
    "248.",  # reserved
    "249.",  # reserved
    "250.",  # reserved
    "251.",  # reserved
    "252.",  # reserved
    "253.",  # reserved
    "254.",  # reserved
    "255.",  # reserved
)

IPWARE_PRIVATE_IPV6_PREFIX = (
    "::",  # Unspecified address
    "::ffff:",  # messages to software
    "2001:10:",  # messages to software
    "2001:20:",  # messages to software
    "2001::",  # TEREDO
    "2001:2::",  # benchmarking
    "2001:db8:",  # reserved for documentation and example code
    "fc00:",  # IPv6 private block
    "fe80:",  # link-local unicast
    "ff00:",  # IPv6 multicast
)

IPWARE_PRIVATE_IP_PREFIX = (
    IPWARE_PRIVATE_IPV4_PREFIX + IPWARE_PRIVATE_IPV6_PREFIX
)

IPWARE_LOOPBACK_IPV4_PREFIX = ("127.",)  # IPv4 loopback device (Host)

IPWARE_LOOPBACK_IPV6_PREFIX = ("::1",)  # IPv6 loopback device (Host)

IPWARE_LOOPBACK_PREFIX = (
    IPWARE_LOOPBACK_IPV4_PREFIX + IPWARE_LOOPBACK_IPV6_PREFIX
)

IPWARE_NON_PUBLIC_IP_PREFIX = IPWARE_PRIVATE_IP_PREFIX + IPWARE_LOOPBACK_PREFIX

# --------------------------------------------------------------------------- #
# BUILD REGEX TRIE OF IPV4 ADDRESSES
# --------------------------------------------------------------------------- #

_tree = Trie()

for ip in IPWARE_PRIVATE_IPV4_PREFIX + IPWARE_LOOPBACK_IPV4_PREFIX:
    _tree.add(ip)

IPWARE_IPV4_REGEX = re.compile("^{}.*".format(_tree.pattern()))


__all__ = (
    "IPWARE_META_PRECEDENCE_ORDER",
    "IPWARE_PRIVATE_IPV4_PREFIX",
    "IPWARE_PRIVATE_IPV6_PREFIX",
    "IPWARE_PRIVATE_IP_PREFIX",
    "IPWARE_LOOPBACK_IPV4_PREFIX",
    "IPWARE_LOOPBACK_IPV6_PREFIX",
    "IPWARE_LOOPBACK_PREFIX",
    "IPWARE_NON_PUBLIC_IP_PREFIX",
)
