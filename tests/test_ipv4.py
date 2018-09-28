from sanic_ipware import get_client_ip


def test_meta_none(create_request):
    request = create_request()
    ip, routable = get_client_ip(request)

    assert ip is None
    assert routable is False


def test_meta_single(create_request):
    request = create_request({
        'X-Forwarded-For': '177.139.233.139, 198.84.193.157, 198.84.193.158',
    })

    result = get_client_ip(request)
    assert result == ("177.139.233.139", True)


def test_meta_multi(create_request):
    request = create_request({
        'X-Forwarded-For': '177.139.233.139, 198.84.193.157, 198.84.193.158',
        'Forwarded-For': '177.139.233.133',
    })
    result = get_client_ip(request)
    assert result == ("177.139.233.139", True)


def test_meta_multi_precedence_order(create_request):
    request = create_request({
        'Forwarded-For': '177.139.233.138, 198.84.193.157, 198.84.193.158',
        'X-Forwarded-For': '177.139.233.139, 198.84.193.157, 198.84.193.158',
        'X-Cluster-Client-IP': '177.139.233.133',
    })
    result = get_client_ip(request)
    assert result == ("177.139.233.139", True)


def test_meta_proxy_order_left_most(create_request):
    request = create_request({
        'X-Forwarded-For': '177.139.233.139, 198.84.193.157, 198.84.193.158',
    })
    result = get_client_ip(request, proxy_order='left-most')
    assert result == ("177.139.233.139", True)


def test_meta_proxy_order_right_most(create_request):
    request = create_request({
        'X-Forwarded-For': '177.139.233.139, 198.84.193.157, 198.84.193.158',
    })
    result = get_client_ip(request, proxy_order='right-most')
    assert result == ("198.84.193.158", True)


def test_meta_multi_precedence_private_first(create_request):
    request = create_request({
        'X-Forwarded-For': '10.0.0.0, 10.0.0.1, 10.0.0.2',
        'X-Cluster-Client-IP': '177.139.233.138, 198.84.193.157, 198.84.193.158',
        'True-Client-IP': '177.139.233.133',
    })
    result = get_client_ip(request)
    assert result == ("177.139.233.138", True)


def test_meta_multi_precedence_invalid_first(create_request):
    request = create_request({
        'X-Forwarded-For': 'unknown, 10.0.0.1, 10.0.0.2',
        'X-Cluster-Client-IP': '177.139.233.138, 198.84.193.157, 198.84.193.158',
        'True-Client-IP': '177.139.233.133',
    })
    result = get_client_ip(request)
    assert result == ("177.139.233.138", True)


def test_meta_error_only(create_request):
    request = create_request({
        'X-Forwarded-For': 'unknown, 177.139.233.139, 198.84.193.157, 198.84.193.158',
    })
    result = get_client_ip(request)
    assert result == (None, False)


def test_meta_error_first(create_request):
    request = create_request({
        'X-Forwarded-For': 'unknown, 177.139.233.139, 198.84.193.157, 198.84.193.158',
        'Forwarded-For': '177.139.233.138, 198.84.193.157, 198.84.193.158',
    })
    result = get_client_ip(request)
    assert result == ("177.139.233.138", True)


def test_meta_singleton(create_request):
    request = create_request({
        'X-Forwarded-For': '177.139.233.139',
    })
    result = get_client_ip(request)
    assert result == ("177.139.233.139", True)


def test_meta_singleton_proxy_count(create_request):
    request = create_request({
        'X-Forwarded-For': '177.139.233.139',
    })
    result = get_client_ip(request, proxy_count=1)
    assert result == (None, False)


def test_meta_singleton_proxy_count_private(create_request):
    request = create_request({
        'X-Forwarded-For': '10.0.0.0',
        'X-Real-IP': '177.139.233.139',
    })
    result = get_client_ip(request, proxy_count=1)
    assert result == (None, False)


def test_meta_singleton_private_fallback(create_request):
    request = create_request({
        'X-Forwarded-For': '10.0.0.0',
        'X-Real-IP': '177.139.233.139',
    })
    result = get_client_ip(request)
    assert result == ("177.139.233.139", True)


def test_meta_proxy_trusted_ips(create_request):
    request = create_request({
        'X-Forwarded-For': '177.139.233.139, 198.84.193.157, 198.84.193.158',
    })
    result = get_client_ip(request, proxy_trusted_ips=['198.84.193.158'])
    assert result == ("177.139.233.139", True)


def test_meta_proxy_trusted_ips_proxy_count(create_request):
    request = create_request({
        'X-Forwarded-For': '177.139.233.139, 198.84.193.157, 198.84.193.158',
    })
    result = get_client_ip(request, proxy_count=2, proxy_trusted_ips=['198.84.193.158'])
    assert result == ("177.139.233.139", True)


def test_meta_proxy_trusted_ips_proxy_count_less_error(create_request):
    request = create_request({
        'X-Forwarded-For': '177.139.233.139, 198.84.193.158',
    })
    result = get_client_ip(request, proxy_count=2, proxy_trusted_ips=['198.84.193.158'])
    assert result == (None, False)


def test_meta_proxy_trusted_ips_proxy_count_more_error(create_request):
    request = create_request({
        'X-Forwarded-For': '177.139.233.139, 198.84.193.157, 198.84.193.158',
    })
    result = get_client_ip(request, proxy_count=1, proxy_trusted_ips=['198.84.193.158'])
    assert result == (None, False)


def test_meta_proxy_trusted_ips_proxy_count_more_error_fallback(create_request):
    request = create_request({
        'X-Forwarded-For': '177.139.233.139, 198.84.193.157, 198.84.193.158',
        'X-Real-IP': '177.139.233.139',
    })
    result = get_client_ip(request, proxy_count=1, proxy_trusted_ips=['198.84.193.158'])
    assert result == (None, False)


def test_best_matched_ip(create_request):
    request = create_request({
        'X-Real-IP': '192.168.1.1',
        'Via': '177.31.233.133',
    })
    ip = get_client_ip(request)
    assert ip == ("177.31.233.133", True)


def test_best_matched_ip_public(create_request):
    request = create_request({
        'X-Real-IP': '177.31.233.122',
        'Via': '177.31.233.133',
    })
    ip = get_client_ip(request)
    assert ip == ("177.31.233.122", True)


def test_best_matched_ip_private(create_request):
    request = create_request({
        'X-Real-IP': '192.168.1.1',
        'Via': '127.0.0.1',
    })
    ip = get_client_ip(request)
    assert ip == ("192.168.1.1", False)


def test_best_matched_ip_private_precedence(create_request):
    request = create_request({
        'X-Real-IP': '127.0.0.1',
        'Via': '192.168.1.1',
    })
    ip = get_client_ip(request)
    assert ip == ("192.168.1.1", False)


def test_100_low_range_public(create_request):
    request = create_request({
        'X-Real-IP': '100.63.0.9',
    })
    ip = get_client_ip(request)
    assert ip == ("100.63.0.9", True)


def test_100_block_private(create_request):
    request = create_request({
        'X-Real-IP': '100.76.0.9',
    })
    ip = get_client_ip(request)
    assert ip == ("100.76.0.9", False)


def test_100_high_range_public(create_request):
    request = create_request({
        'X-Real-IP': '100.128.0.9',
    })
    ip = get_client_ip(request)
    assert ip == ("100.128.0.9", True)


def test_request_header_order_specific(create_request):
    request = create_request({
        'X-Real-IP': '192.168.1.1',
        'Via': '177.139.233.139',
        'X-Forwarded-For': '177.139.233.139, 198.84.193.157, 198.84.193.158',
    })
    ip = get_client_ip(request, request_header_order=['X-Forwarded-For'])
    assert ip == ("177.139.233.139", True)


def test_request_header_order_multiple(create_request):
    request = create_request({
        'X-Forwarded-For': '177.139.233.139, 198.84.193.157, 198.84.193.158',
        'Forwarded-For': '177.139.233.138, 198.84.193.157, 198.84.193.158',
        'Via': '177.139.233.133',
    })
    ip = get_client_ip(request, request_header_order=['Forwarded-For', 'X-Forwarded-For'])
    assert ip == ("177.139.233.138", True)
