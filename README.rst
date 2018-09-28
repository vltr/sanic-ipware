=================
``sanic-ipware``
=================

.. start-badges

.. image:: https://img.shields.io/pypi/status/sanic-ipware.svg
    :alt: PyPI - Status
    :target: https://pypi.org/project/sanic-ipware/

.. image:: https://img.shields.io/pypi/v/sanic-ipware.svg
    :alt: PyPI Package latest release
    :target: https://pypi.org/project/sanic-ipware/

.. image:: https://img.shields.io/pypi/pyversions/sanic-ipware.svg
    :alt: Supported versions
    :target: https://pypi.org/project/sanic-ipware/

.. image:: https://travis-ci.org/vltr/sanic-ipware.svg?branch=master
    :alt: Travis-CI Build Status
    :target: https://travis-ci.org/vltr/sanic-ipware

.. image:: https://codecov.io/github/vltr/sanic-ipware/coverage.svg?branch=master
    :alt: Coverage Status
    :target: https://codecov.io/github/vltr/sanic-ipware

.. end-badges

This is a fork of `django-ipware <https://github.com/un33k/django-ipware>`_ to work with `Sanic <https://sanicframework.org/>`_.

Overview
--------

**Best attempt** to get client's IP address while keeping it **DRY**.

Notice
------

There is no real good "out-of-the-box" solution against fake IP addresses, aka "IP Address Spoofing". You are encouraged to read the `Advanced users <README.rst#advanced-users>`_ section of this page and use ``trusted_proxies_ips`` and/or ``proxy_count`` features to match your needs, especially *if* you are planning to include ``sanic-ipware`` in any authentication, security or "anti-fraud" related architecture.

How to install
--------------

The best way to install ``sanic-ipware`` would be using ``pip``:

.. code-block::

    pip install sanic-ipware

How to use
----------

There's basically one method that should be usable from ``sanic_ipware``, called ``get_client_ip``. The result is a ``Tuple[Optional[str], bool]`` of ``(ipaddr, routable)``.

.. code-block:: python

    from sanic_ipware import get_client_ip

    @app.get("/some/handler")
    async def somehandler(request):
        ip, routable = get_client_ip(request)
        if ip is not None:
            if routable:
                # we have a (probably) real, public ip address for user
            else:
                # we have ip address, but it might not be public routable
        else:
            # we don't have a ip address for the user

Advanced users
--------------

.. code-block:: python

    # you can provide your own meta precedence order by using the
    # request_header_order in the function call:
    ip, routable = get_client_ip(
        request,
        request_header_order=['Forwarded-For', 'X-Forwarded-For'])

    # if you're going to do this a lot, wrap the function somewhere with
    # functools.partial
    from functools import partial
    my_get_client_ip = partial(
        get_client_ip,
        request_header_order=['Forwarded-For', 'X-Forwarded-For'])
    ip, routable = my_get_client_ip(request)

    # if you plan to use sanic_ipware in any authentication, security or
    # "anti-fraud" related architecture, you should configure it to only
    # "trust" one or more "known" proxy server(s)), in the function call:
    ip, routable = get_client_ip(request, proxy_trusted_ips=['198.84.193.158'])

    # you can perform the same functools.partial trick with these trusted IPs

License
-------

MIT, the same as ``django-ipware`` `license <https://github.com/un33k/django-ipware/blob/57897c03026913892e61a164bc8b022778802ab9/LICENSE>`_ .
