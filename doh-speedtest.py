#!/usr/bin/python
import base64
import concurrent.futures
import struct
import time
from typing import List, Tuple, Union

import httpx  # pip install "httpx[http2]"

timeout = 3.0
target_domain = "google.com"

"""
https://dnsprivacy.org/public_resolvers/#dns-over-https-doh
https://dnscrypt.info/public-servers/
https://dnscrypt.info/map/
"""
doh_servers = [
    "https://223.5.5.5/dns-query",
    # "https://1.12.12.12/dns-query",  # https://docs.dnspod.cn/notices/mian-fei-ban-dot-dohbu-zai-gong-kai-ipjie-ru-de-gong-gao/
    "https://dns.alidns.com/dns-query",
    "https://doh.pub/dns-query",
    "https://doh.360.cn/dns-query",
    "https://dns.cloudflare.com/dns-query",
    "https://cloudflare-dns.com/dns-query",
    "https://1.1.1.1/dns-query",
    "https://1.0.0.1/dns-query",
    "https://dns.google/dns-query",  # RFC 8484 (GET and POST)
    "https://dns.google/resolve?",  # JSON API (GET)
    "https://8.8.8.8/dns-query",
    "https://8.8.4.4/dns-query",
    "https://dns.quad9.net/dns-query",  # IBM
    "https://9.9.9.9/dns-query",
    "https://149.112.112.112/dns-query",
    "https://dns.adguard-dns.com/dns-query",
    "https://unfiltered.adguard-dns.com/dns-query",
    "https://dns.twnic.tw/dns-query",
    "https://101.101.101.101/dns-query",
    "https://doh.opendns.com/dns-query",  # Cisco
    "https://208.67.222.222/dns-query",
    "https://doh.sb/dns-query",
    "https://doh.dns.sb/dns-query",
    "https://45.11.45.11/dns-query",
    "https://185.222.222.222/dns-query",
    # "https://ada.openbld.net/dns-query",  # Fast and flexible adaptive filtering... edith.xiaohongshu.com --> [0.0.0.0 ::]
    # "https://private.canadianshield.cira.ca/dns-query",  # https://www.cira.ca/en/canadian-shield/
    "https://sky.rethinkdns.com/dns-query",
    # "https://dns-doh.dnsforfamily.com/dns-query",  # These servers block **porn and other adult websites**, and ..., while ... from **malware, ads, gambling**.
    "https://dns.switch.ch/dns-query",  # https://portal.switch.ch/pub/public-dns **within** Switzerland.
    "https://dnspub.restena.lu/dns-query",  # https://www.restena.lu/en/service/public-dns-resolver
    "https://anycast.uncensoreddns.org/dns-query",
    "https://doh.applied-privacy.net/query",  # We do not provide DNS filter services, our resolvers ... from the authoritative DNS servers.
    "https://wikimedia-dns.org/dns-query",
    "https://freedns.controld.com/p0",
    "https://public.dns.iij.jp/dns-query",  # https://policy.public.dns.iij.jp/
    "https://101.6.6.6:8443/dns-query",  # https://tuna.moe/help/dns/
    "https://common.dot.dns.yandex.net",
    "https://77.88.8.8/dns-query",  # yandex
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
        headers = {"Accept": "application/dns-message", "User-Agent": ""}
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
            "User-Agent": "",
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
        headers = {"Accept": "application/dns-json", "User-Agent": ""}
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


available_servers: List[Tuple[str, float]] = []

print("DoH Server Connectivity Results:")


def worker(url: str) -> str:
    if isinstance(elapsed_time := test_doh_server(url), float):
        available_servers.append((url, elapsed_time))  # first come first appended
        return f"[*] {url.ljust(pad_len)}: Connected in {elapsed_time * 1e3:.2f} ms"
    else:
        return f"[!] {url.ljust(pad_len)}: {elapsed_time}"


with concurrent.futures.ThreadPoolExecutor(max_workers=len(doh_servers)) as executor:
    results = list(executor.map(lambda u: worker(u), doh_servers))
    for res in results:
        if res is not None:
            print(res)
    print("\nAvailable DoH servers (sorted):")
    available_servers.sort(key=lambda server_tuple: server_tuple[1])
    for server, elapsed_time in available_servers:
        print(f"{server.ljust(pad_len)}: {elapsed_time * 1e3:.2f} ms")
