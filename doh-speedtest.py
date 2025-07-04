#!/usr/bin/python
import base64
import concurrent.futures
import struct
import time
from typing import Union

import httpx  # pip install "httpx[http2]"

timeout = 2
target_domain = "google.com"

doh_servers = [
    "https://dns.alidns.com/dns-query",
    "https://doh.pub/dns-query",
    "https://doh.360.cn/dns-query",
    "https://dns.cloudflare.com/dns-query",
    "https://cloudflare-dns.com/dns-query",
    "https://dns.google/dns-query",
    "https://dns.quad9.net/dns-query",
    "https://149.112.112.112/dns-query",  # Quad9
    "https://dns.twnic.tw/dns-query",  # Quad101
    "https://doh.opendns.com/dns-query",
    "https://208.67.222.222/dns-query",  # OpenDNS
    "https://doh.dns.sb/dns-query",
    "https://ada.openbld.net/dns-query",
    "https://private.canadianshield.cira.ca/dns-query",
    "https://sky.rethinkdns.com/dns-query",
    "https://dns-doh.dnsforfamily.com/dns-query",
    "https://dns.switch.ch/dns-query",
    "https://dnspub.restena.lu/dns-query",
    "https://anycast.uncensoreddns.org/dns-query",
    "https://doh.applied-privacy.net/query",
]

pad_len = max(len(url) for url in doh_servers) + 1


def build_wire(domain: str) -> bytes:
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


def test_doh_server_wire(url: str) -> Union[float, str]:
    try:
        dns_query = build_wire(target_domain)
        dns_query_b64 = base64.urlsafe_b64encode(dns_query).rstrip(b"=").decode()
        headers = {"Accept": "application/dns-message"}
        start_time = time.time()
        with httpx.Client(http2=True, timeout=timeout) as client:
            response = client.get(url, params={"dns": dns_query_b64}, headers=headers)
            response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        return time.time() - start_time
    except httpx.HTTPStatusError as e:
        return f"HTTPStatusError: {e.response.status_code} - {e.response.text.strip()}"
    except Exception as e:
        return f"{type(e).__name__}: {e}"


def test_doh_server_wire_post(url: str) -> Union[float, str]:
    try:
        dns_query = build_wire(target_domain)
        headers = {
            "Content-Type": "application/dns-message",
            "Accept": "application/dns-message",
        }
        start_time = time.time()
        with httpx.Client(http2=True, timeout=timeout) as client:
            response = client.post(url, content=dns_query, headers=headers)
            response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        return time.time() - start_time
    except httpx.HTTPStatusError as e:
        return f"HTTPStatusError: {e.response.status_code} - {e.response.text.strip()}"
    except Exception as e:
        return f"{type(e).__name__}: {e}"


def test_doh_server_json(url: str) -> Union[float, str]:
    try:
        headers = {"Accept": "application/dns-json"}
        start_time = time.time()
        with httpx.Client(http2=True, timeout=timeout) as client:
            response = client.get(
                url, params={"name": target_domain, "type": "A"}, headers=headers
            )
            response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        return time.time() - start_time
    except httpx.HTTPStatusError as e:
        return f"HTTPStatusError: {e.response.status_code} - {e.response.text.strip()}"
    except Exception as e:
        return f"{type(e).__name__}: {e}"


def test_doh_server(url: str) -> Union[float, str]:
    if isinstance(wire_result := test_doh_server_wire(url), float):
        return wire_result
    elif isinstance(wire_post_result := test_doh_server_wire_post(url), float):
        return wire_post_result
    elif isinstance(json_result := test_doh_server_json(url), float):
        return json_result
    else:
        return (
            f"(WIRE GET ) {wire_result};\n"
            f"{' ' * (pad_len + len('[ ] : '))}(WIRE POST) {wire_post_result};\n"
            f"{' ' * (pad_len + len('[ ] : '))}(JSON API ) {json_result}."
        )


print("DoH Server Connectivity Results (wire format):")


def worker(url) -> str:
    if isinstance(elapsed_time := test_doh_server(url), float):
        return f"[*] {url.ljust(pad_len)}: Connected in {elapsed_time * 1e3:.2f} ms"
    else:
        return f"[!] {url.ljust(pad_len)}: {elapsed_time}"


with concurrent.futures.ThreadPoolExecutor(max_workers=len(doh_servers)) as executor:
    results = list(executor.map(lambda u: worker(u), doh_servers))
    for res in results:
        if res is not None:
            print(res)
