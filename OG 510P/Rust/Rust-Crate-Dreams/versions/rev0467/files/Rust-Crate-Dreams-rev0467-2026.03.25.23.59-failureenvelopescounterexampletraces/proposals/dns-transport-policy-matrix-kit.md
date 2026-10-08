---
id: P-0162
title: DNS Transport & Policy Matrix Kit
status: idea
domains: [networking, dns, security, privacy, observability, conformance]
last_reviewed: 2026-03-05
evidence:
  - https://bluejekyll.github.io/blog/posts/announcing-hickory-dns/
  - https://github.com/hickory-dns/hickory-dns
  - https://hickory-dns.org/
  - https://doc.rust-lang.org/cargo/reference/config.html
---

# Problem

Rust has strong DNS building blocks (notably **Hickory DNS**, formerly Trust-DNS), including modern transports (DoT/DoH/DoQ and even DoH3 in packaging ecosystems). But shipping DNS inside an application (or as a sidecar) is still *surprisingly hard*:

- Apps need **policy**, not just a resolver: which transports are allowed, how to fall back, which endpoints to pin, when to validate DNSSEC, how to handle captive portals.
- Operational questions (latency, cache hit rates, NXDOMAIN storms, SERVFAIL causes) are hard to answer without consistent observability.
- Transport matrix issues are hard to reproduce: “DoQ fails on this network, DoH works, DoT flaps” rarely comes with evidence.

We’re missing a crate/tooling layer that makes DNS configuration, evidence capture, and conformance **standardized and shareable**.

# What it should provide

## 1) A policy-first DNS configuration model

A small, explicit policy schema (e.g., `dns-policy.toml`) that describes:

- Allowed transports and order: `udp53`, `dot`, `doh`, `doq`, `doh3`
- Endpoints: bootstrap IPs, SNI/ALPN, pinned certificates/SPKI (optional)
- DNSSEC policy: required/optional/off; trust anchor handling
- Caching policy: TTL caps/floors, negative caching rules
- Privacy policy: QNAME minimization toggle, ECS policy, query padding

Goal: a single policy file can drive resolvers across apps, and can be audited.

## 2) Evidence bundles: `dnsmatrixbundle.zip`

A portable artifact that captures “what happened” without exfiltrating sensitive query names:

- `policy.toml` (redacted if needed)
- `transports/` (attempt logs per transport)
- `metrics.json` (latencies, error codes, retries, cache stats)
- `pcap/` optional capture pointers (or hashes)
- `redaction.json` rules applied

## 3) `cargo dns doctor`

A cargo-native UX for apps embedding DNS:

- `cargo dns doctor` — connectivity probes and policy sanity checks
- `cargo dns matrix` — run a matrix across transports/endpoints and summarize
- `cargo dns bundle` — capture a `dnsmatrixbundle.zip` from a run

Integrate with Cargo config conventions (e.g., profiles or `.cargo/config.toml` overlays) for easy CI vs local modes.

## 4) Resolver adapters

- Start with a Hickory-based adapter (stub resolver / forwarding resolver)
- Optional adapters for system resolvers (read-only) to compare behavior

## 5) Conformance suites

- Known test domains + expected behavior under DNSSEC on/off
- Transport degradation scenarios (blocked UDP 53, blocked QUIC, broken TLS MITM)
- Regression packs that ensure policy behavior is stable across versions

# MVP scope (2–4 weeks)

- `dns-policy.toml` schema v0 (transports, endpoints, fallback, basic caching)
- Hickory adapter: do basic query path with policy-controlled transport order
- `cargo dns bundle` to emit `dnsmatrixbundle.zip` with redaction support

# v1 scope (2–3 months)

- DNSSEC policy wiring + trust anchor support
- DoH3/DoQ richer instrumentation
- CI matrix runner + baseline comparison (`dnsmatrix diff`)
- Prebuilt “profiles” (privacy-first, speed-first, enterprise-proxy)

# Why this is an “epic” crate

It upgrades DNS-in-app from “library call” to a **portable, testable, observable subsystem** with an evidence contract—exactly the sort of missing “ops layer” that helps Rust deployments succeed.
