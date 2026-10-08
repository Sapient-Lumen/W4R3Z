#!/usr/bin/env python3
"""Endpoint validator skeleton (v20)

Multi-perspective endpoint validation is meant to detect:
- DNS tampering / poisoning / split-horizon answers
- BGP diversion that changes certificate or content
- CDN split delivery (different bodies/hashes by region)

In production, perspectives should be gathered from:
- independent monitors in different ASNs
- optional external networks (e.g., RIPE Atlas probes)

This script is a placeholder that validates from the *local* perspective only.
"""

import argparse, json, hashlib, ssl, socket
from urllib.parse import urlparse
from urllib.request import urlopen, Request

def sha256_hex(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def fetch_https(url: str, timeout: int = 10) -> tuple[int, dict, bytes]:
    req = Request(url)
    with urlopen(req, timeout=timeout) as resp:
        return getattr(resp, "status", 200), dict(resp.headers.items()), resp.read()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    u = urlparse(args.url)
    host = u.hostname
    port = u.port or 443

    ctx = ssl.create_default_context()
    with socket.create_connection((host, port), timeout=10) as sock:
        with ctx.wrap_socket(sock, server_hostname=host) as ssock:
            cert = ssock.getpeercert(binary_form=True)
            cert_hash = sha256_hex(cert)

    status, headers, body = fetch_https(args.url)
    report = {
        "schema_version": "1.0",
        "timestamp": "TODO",
        "target": args.url,
        "perspectives": [{
            "id": "local",
            "dns": None,
            "tls": {"spki_fingerprint": None, "cert_chain_hash": cert_hash},
            "http": {"status": status, "body_hash": sha256_hex(body), "headers_hash": sha256_hex(json.dumps(headers, sort_keys=True).encode("utf-8"))}
        }],
        "quorum_rule": "local-only (placeholder)",
        "decision": "inconclusive",
        "notes": "Collect multiple independent perspectives in production.",
        "signatures": []
    }
    json.dump(report, open(args.out,"w",encoding="utf-8"), indent=2)

if __name__ == "__main__":
    main()
