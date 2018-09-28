from sanic_ipware import utils as util


def test_is_valid_ip():
    ip = "177.139.233.139"
    assert util.is_valid_ip(ip)

    ip = "3ffe:1900:4545:3:200:f8ff:fe21:67cf"
    assert util.is_valid_ip(ip)


def test_is_invalid_ip():
    ip = "177.139.233.139x"
    assert util.is_valid_ip(ip) is False

    ip = "3ffe:1900:4545:3:200:f8ff:fe21:67cz"
    assert util.is_valid_ip(ip) is False


def test_is_private_ip():
    ip = "127.0.0.1"
    assert util.is_private_ip(ip)

    ip = "::1/128"
    assert util.is_private_ip(ip)


def test_is_public_ip():
    ip = "177.139.233.139"
    assert util.is_public_ip(ip)

    ip = "74dc::02ba"
    assert util.is_public_ip(ip)


def test_is_loopback_ip():
    ip = "127.0.0.1"
    assert util.is_loopback_ip(ip)

    ip = "177.139.233.139"
    assert util.is_loopback_ip(ip) is False

    ip = "10.0.0.1"
    assert util.is_loopback_ip(ip) is False

    ip = "::1/128"
    assert util.is_loopback_ip(ip)

    ip = "74dc::02ba"
    assert util.is_loopback_ip(ip) is False

    ip = "2001:db8:"
    assert util.is_loopback_ip(ip) is False


def test_http_request_meta_headers(create_request):
    ip_str = "192.168.255.182, 10.0.0.0, 127.0.0.1, 198.84.193.157, 177.139.233.139,"
    request = create_request({"X-Forwarded-For": ip_str})
    value = util.get_request_header(request, "X-Forwarded-For")
    assert value == ip_str


def test_ips_from_strings():
    ip_str = "192.168.255.182, 198.84.193.157, 177.139.233.139 ,"
    result = util.get_ips_from_string(ip_str)
    assert result == (
        ["192.168.255.182", "198.84.193.157", "177.139.233.139"],
        3,
    )


def test_get_ip_info():
    ip = "127.0.0.1"
    result = util.get_ip_info(ip)
    assert result == (ip, False)

    ip = "10.0.0.1"
    result = util.get_ip_info(ip)
    assert result == (ip, False)

    ip = "74dc::02ba"
    result = util.get_ip_info(ip)
    assert result == (ip, True)
