from sanic_ipware import get_client_ip


def test_meta_none(create_request):
    request = create_request()
    ip, routable = get_client_ip(request)
    assert ip is None
    assert routable is False


def test_meta_single(create_request):
    request = create_request(
        {"X-Forwarded-For": "3ffe:1900:4545:3:200:f8ff:fe21:67cf, 74dc::02ba"}
    )
    result = get_client_ip(request)
    assert result == ("3ffe:1900:4545:3:200:f8ff:fe21:67cf", True)


def test_meta_multi(create_request):
    request = create_request(
        {
            "X-Forwarded-For": "3ffe:1900:4545:3:200:f8ff:fe21:67cf, 74dc::02ba, 74dc::02bb",
            "Via": "74dc::02bc",
        }
    )
    result = get_client_ip(request)
    assert result == ("3ffe:1900:4545:3:200:f8ff:fe21:67cf", True)


def test_meta_multi_precedence_order(create_request):
    request = create_request(
        {
            "Forwarded-For": "74dc::02be, 74dc::02bf",
            "X-Forwarded-For": "3ffe:1900:4545:3:200:f8ff:fe21:67cf, 74dc::02ba, 74dc::02bb",
            "Via": "74dc::02bc",
        }
    )
    result = get_client_ip(request)
    assert result == ("3ffe:1900:4545:3:200:f8ff:fe21:67cf", True)


def test_meta_proxy_order_left_most(create_request):
    request = create_request(
        {
            "X-Forwarded-For": "3ffe:1900:4545:3:200:f8ff:fe21:67cf, 74dc::02ba, 74dc::02bb"
        }
    )
    result = get_client_ip(request, proxy_order="left-most")
    assert result == ("3ffe:1900:4545:3:200:f8ff:fe21:67cf", True)


def test_meta_proxy_order_right_most(create_request):
    request = create_request(
        {
            "X-Forwarded-For": "3ffe:1900:4545:3:200:f8ff:fe21:67cf, 74dc::02ba, 74dc::02bb"
        }
    )
    result = get_client_ip(request, proxy_order="right-most")
    assert result == ("74dc::02bb", True)


def test_meta_multi_precedence_private_first(create_request):
    request = create_request(
        {
            "X-Forwarded-For": "2001:db8:, ::1",
            "Forwarded-For": "3ffe:1900:4545:3:200:f8ff:fe21:67cf, 74dc::02ba, 74dc::02bb",
            "Via": "74dc::02bc",
        }
    )
    result = get_client_ip(request)
    assert result == ("3ffe:1900:4545:3:200:f8ff:fe21:67cf", True)


def test_meta_multi_precedence_invalid_first(create_request):
    request = create_request(
        {
            "X-Forwarded-For": "unknown, 2001:db8:, ::1",
            "Forwarded-For": "3ffe:1900:4545:3:200:f8ff:fe21:67cf, 74dc::02ba, 74dc::02bb",
            "Via": "74dc::02bc",
        }
    )
    result = get_client_ip(request)
    assert result == ("3ffe:1900:4545:3:200:f8ff:fe21:67cf", True)


def test_meta_error_only(create_request):
    request = create_request(
        {
            "Forwarded-For": "unknown, 3ffe:1900:4545:3:200:f8ff:fe21:67cf, 74dc::02ba, 74dc::02bb"
        }
    )
    result = get_client_ip(request)
    assert result == (None, False)


def test_meta_error_first(create_request):
    request = create_request(
        {
            "X-Forwarded-For": "unknown, 3ffe:1900:4545:3:200:f8ff:fe21:67cf, 74dc::02ba, 74dc::02bb",
            "Forwarded-For": "3ffe:1900:4545:3:200:f8ff:fe21:67cf, 74dc::02ba, 74dc::02bb",
        }
    )
    result = get_client_ip(request)
    assert result == ("3ffe:1900:4545:3:200:f8ff:fe21:67cf", True)


def test_meta_singleton(create_request):
    request = create_request(
        {"X-Forwarded-For": "3ffe:1900:4545:3:200:f8ff:fe21:67cf"}
    )
    result = get_client_ip(request)
    assert result == ("3ffe:1900:4545:3:200:f8ff:fe21:67cf", True)


def test_meta_singleton_proxy_count(create_request):
    request = create_request(
        {
            "X-Forwarded-For": "3ffe:1900:4545:3:200:f8ff:fe21:67cf",
            "X-Real-IP": "74dc::02ba",
        }
    )
    result = get_client_ip(request, proxy_count=1)
    assert result == (None, False)


def test_meta_singleton_proxy_count_private(create_request):
    request = create_request(
        {
            "X-Forwarded-For": "::1",
            "X-Real-IP": "3ffe:1900:4545:3:200:f8ff:fe21:67cf",
        }
    )
    result = get_client_ip(request, proxy_count=1)
    assert result == (None, False)


def test_meta_singleton_private_fallback(create_request):
    request = create_request(
        {
            "X-Forwarded-For": "::1",
            "X-Real-IP": "3ffe:1900:4545:3:200:f8ff:fe21:67cf",
        }
    )
    result = get_client_ip(request)
    assert result == ("3ffe:1900:4545:3:200:f8ff:fe21:67cf", True)


def test_meta_proxy_trusted_ips(create_request):
    request = create_request(
        {
            "X-Forwarded-For": "3ffe:1900:4545:3:200:f8ff:fe21:67cf, 74dc::02ba, 74dc::02bb"
        }
    )
    result = get_client_ip(request, proxy_trusted_ips=["74dc::02bb"])
    assert result == ("3ffe:1900:4545:3:200:f8ff:fe21:67cf", True)


def test_meta_proxy_trusted_ips_proxy_count(create_request):
    request = create_request(
        {
            "X-Forwarded-For": "3ffe:1900:4545:3:200:f8ff:fe21:67cf, 74dc::02ba, 74dc::02bb"
        }
    )
    result = get_client_ip(
        request, proxy_count=2, proxy_trusted_ips=["74dc::02bb"]
    )
    assert result == ("3ffe:1900:4545:3:200:f8ff:fe21:67cf", True)


def test_meta_proxy_trusted_ips_proxy_count_less_error(create_request):
    request = create_request(
        {"X-Forwarded-For": "3ffe:1900:4545:3:200:f8ff:fe21:67cf, 74dc::02bb"}
    )
    result = get_client_ip(
        request, proxy_count=2, proxy_trusted_ips=["74dc::02bb"]
    )
    assert result == (None, False)


def test_meta_proxy_trusted_ips_proxy_count_more_error(create_request):
    request = create_request(
        {
            "X-Forwarded-For": "3ffe:1900:4545:3:200:f8ff:fe21:67cf, 74dc::02ba, 74dc::02bb"
        }
    )
    result = get_client_ip(
        request, proxy_count=1, proxy_trusted_ips=["74dc::02bb"]
    )
    assert result == (None, False)


def test_meta_proxy_trusted_ips_proxy_count_more_error_ignore_fallback(
    create_request
):
    request = create_request(
        {
            "X-Forwarded-For": "3ffe:1900:4545:3:200:f8ff:fe21:67cf, 74dc::02ba, 74dc::02bb",
            "X-Real-IP": "74dc::02bb",
        }
    )
    result = get_client_ip(
        request, proxy_count=1, proxy_trusted_ips=["74dc::02bb"]
    )
    assert result == (None, False)
