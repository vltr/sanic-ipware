import typing as t

from . import defaults as defs
from . import utils as util


def get_client_ip(
    request: object,
    proxy_order: str='left-most',
    proxy_count: int=None,
    proxy_trusted_ips: t.List[str]=None,
    request_header_order: t.Optional[t.Union[t.List[str], t.Tuple[str]]]=None,
) -> t.Tuple[t.Optional[str], bool]:
    client_ip = None
    routable = False

    if proxy_count is None:
        proxy_count = -1

    if proxy_trusted_ips is None:
        proxy_trusted_ips = []

    if request_header_order is None:
        request_header_order = defs.IPWARE_META_PRECEDENCE_ORDER

    for header in request_header_order:
        value = util.get_request_header(request, header)
        if value:
            ips, ip_count = util.get_ips_from_string(value)

            if ip_count < 1:
                # we are expecting at least one IP address to process
                continue

            if proxy_count == 0 and ip_count > 1:
                # we are not expecting requests via any proxies
                continue

            if proxy_count > 0 and proxy_count != ip_count - 1:
                # we are expecting requests via `proxy_count` number of proxies
                continue

            if proxy_trusted_ips and ip_count < 2:
                # we are expecting requests via at least one trusted proxy
                continue

            if proxy_order == 'right-most' and ip_count > 1:
                # we are expecting requests via proxies to be custom as per
                # `<proxy2>, <proxy1>, <client>`
                ips.reverse()

            if proxy_trusted_ips:
                for proxy in proxy_trusted_ips:
                    if proxy in ips[-1]:
                        client_ip, routable = util.get_ip_info(ips[0])
                        if client_ip and routable:
                            return client_ip, routable
            else:
                client_ip, routable = util.get_ip_info(util.get_best_ip(client_ip, ips[0]))
                if client_ip and routable:
                    return client_ip, routable

    return client_ip, routable
