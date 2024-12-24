#!/usr/bin/python
import http.client
import time
from typing import Optional
from urllib.parse import urlencode, urlparse

timeout = 2
target_domain = "google.com"

doh_servers = [
    "https://dns.alidns.com/resolve",
    "https://doh.pub/dns-query",
    "https://doh.360.cn/dns-query",
    "https://dns.cloudflare.com/dns-query",
    "https://dns.quad9.net/dns-query",
    "https://doh.opendns.com/dns-query",
    "https://doh.dns.sb/dns-query",
    "https://ada.openbld.net/dns-query",
]


def test_doh_server(url: str) -> Optional[float]:
    try:
        parsed_url = urlparse(url)
        conn = http.client.HTTPSConnection(parsed_url.netloc, timeout=timeout)
        params = urlencode({"name": target_domain, "type": "A"})
        headers = {"Accept": "application/dns-json"}
        start_time = time.time()
        conn.request("GET", f"{parsed_url.path}?{params}", headers=headers)
        response = conn.getresponse()
        if response.status == 200:
            return time.time() - start_time
        else:
            return None
    except http.client.HTTPException as http_err:  # noqa: F841
        # print(f"HTTP exception occurred for {url}: {http_err}")
        return None
    except Exception as e:  # noqa: F841
        # print(e)
        return None


print("DoH Server Connectivity Results:")
for url in doh_servers:
    elapsed_time = test_doh_server(url)
    if elapsed_time is not None:
        print(f"{url}: Connected in {elapsed_time:.3f} seconds")
    else:
        print(f"{url}: Connection failed")
