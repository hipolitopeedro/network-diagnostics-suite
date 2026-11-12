#!/usr/bin/env python3
"""
network_scanner.py
EN: Concurrent TCP port scanner, latency profiler, and DNS resolution tester for IT infrastructure.
PT: Scanner concorrente de portas TCP, medidor de latência e testador de DNS para infraestrutura de TI.
"""

import argparse
import json
import socket
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from typing import Dict, List, Optional

COMMON_INFRA_PORTS: Dict[int, str] = {
    22: "SSH",
    53: "DNS",
    80: "HTTP",
    88: "Kerberos",
    135: "RPC",
    389: "LDAP",
    443: "HTTPS",
    445: "SMB",
    636: "LDAPS",
    3389: "RDP",
}


def resolve_host(host: str) -> Optional[str]:
    """Resolves a hostname to an IPv4 address."""
    try:
        return socket.gethostbyname(host)
    except socket.gaierror:
        return None


def check_tcp_port(ip: str, port: int, timeout: float = 1.5) -> Dict[str, object]:
    """Tests TCP connectivity to a target IP and port, measuring handshake latency in ms."""
    service = COMMON_INFRA_PORTS.get(port, "Custom")
    start = time.perf_counter()
    try:
        with socket.create_connection((ip, port), timeout=timeout):
            latency_ms = round((time.perf_counter() - start) * 1000, 2)
            return {"port": port, "service": service, "status": "OPEN", "latency_ms": latency_ms}
    except (socket.timeout, ConnectionRefusedError, OSError):
        return {"port": port, "service": service, "status": "CLOSED/FILTERED", "latency_ms": None}


def audit_host(host: str, ports: List[int], timeout: float) -> Dict[str, object]:
    """Runs DNS resolution and concurrent port checks for a single host."""
    resolved_ip = resolve_host(host)
    if not resolved_ip:
        return {
            "host": host,
            "resolved_ip": None,
            "dns_status": "FAILED",
            "ports": [],
        }

    port_results = []
    with ThreadPoolExecutor(max_workers=min(len(ports), 16)) as executor:
        futures = {executor.submit(check_tcp_port, resolved_ip, p, timeout): p for p in ports}
        for future in as_completed(futures):
            port_results.append(future.result())

    port_results.sort(key=lambda x: int(x["port"]))
    return {
        "host": host,
        "resolved_ip": resolved_ip,
        "dns_status": "OK",
        "ports": port_results,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="IT Infrastructure TCP Port & DNS Diagnostics Tool (EN/PT-BR)"
    )
    parser.add_argument(
        "--hosts",
        nargs="+",
        required=True,
        help="Target hostnames or IPv4 addresses (e.g., 1.1.1.1 dc01.corp.local)",
    )
    parser.add_argument(
        "--ports",
        nargs="+",
        type=int,
        default=list(COMMON_INFRA_PORTS.keys()),
        help="TCP ports to check (default: common infrastructure & AD ports)",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=1.5,
        help="Socket connection timeout in seconds (default: 1.5)",
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Optional path to save JSON diagnostic report",
    )
    args = parser.parse_args()

    print("=" * 68)
    print("  NETWORK INFRASTRUCTURE DIAGNOSTICS SUITE")
    print(f"  Timestamp: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print("=" * 68)

    report = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "results": [],
    }

    for host in args.hosts:
        result = audit_host(host, args.ports, args.timeout)
        report["results"].append(result)

        print(f"\n[*] Target: {host} -> IP: {result['resolved_ip'] or 'UNRESOLVED'} (DNS: {result['dns_status']})")
        if result["dns_status"] != "OK":
            continue

        for p in result["ports"]:
            latency_str = f"{p['latency_ms']} ms" if p["latency_ms"] is not None else "-"
            print(f"    Port {p['port']:<5} ({p['service']:<10}) : {p['status']:<16} | Latency: {latency_str}")

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        print(f"\n[OK] JSON diagnostic report saved to: {args.output}")


if __name__ == "__main__":
    main()
