#!/usr/bin/python
import base64
import concurrent.futures
import http.client
import struct
import time
from typing import Optional
from urllib.parse import urlparse

timeout = 2
target_domain = "google.com"

doh_servers = [
    "https://dns.alidns.com/dns-query",
    "https://doh.pub/dns-query",
    "https://doh.360.cn/dns-query",
    "https://dns.cloudflare.com/dns-query",
    "https://dns.quad9.net/dns-query",
    "https://doh.opendns.com/dns-query",
    "https://doh.dns.sb/dns-query",
    "https://ada.openbld.net/dns-query",
]


def build_dns_query(domain: str) -> bytes:
    # 构造最简单的A记录查询报文（递归查询，1个问题）
    tid = 0x1234
    flags = 0x0100  # 标准查询，递归
    qdcount = 1
    ancount = nscount = arcount = 0
    header = struct.pack(">HHHHHH", tid, flags, qdcount, ancount, nscount, arcount)
    # 构造问题部分
    qname = (
        b"".join((bytes([len(x)]) + x.encode() for x in domain.split("."))) + b"\x00"
    )
    qtype = 1  # A
    qclass = 1  # IN
    question = qname + struct.pack(">HH", qtype, qclass)
    return header + question


def test_doh_server_wire(url: str) -> Optional[float]:
    try:
        parsed_url = urlparse(url)
        conn = http.client.HTTPSConnection(parsed_url.netloc, timeout=timeout)
        dns_query = build_dns_query(target_domain)
        dns_query_b64 = base64.urlsafe_b64encode(dns_query).rstrip(b"=").decode()
        path = f"{parsed_url.path}?dns={dns_query_b64}"
        headers = {"Accept": "application/dns-message"}
        start_time = time.time()
        conn.request("GET", path, headers=headers)
        response = conn.getresponse()
        if response.status == 200:
            return time.time() - start_time
        else:
            return None
    except Exception:
        return None


print("DoH Server Connectivity Results (wire format):")


def worker(url):
    elapsed_time = test_doh_server_wire(url)
    pad_len = max(len(url) for url in doh_servers) + 1
    if elapsed_time is not None:
        return f"{url.ljust(pad_len)}: Connected in {elapsed_time:.3f} seconds"
    else:
        return f"{url.ljust(pad_len)}: Connection failed"


with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
    results = list(executor.map(lambda u: worker(u), doh_servers))
    for res in results:
        print(res)
