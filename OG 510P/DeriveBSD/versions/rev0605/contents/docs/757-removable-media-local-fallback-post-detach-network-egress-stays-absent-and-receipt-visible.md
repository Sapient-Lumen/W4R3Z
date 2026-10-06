# Removable-media local fallback post-detach network egress stays absent and receipt-visible

**Tier:** B (Implementation-shaping cut)  
**Profiles:** B, C  
**Pillars:** isolation, reproducibility, operability  
**Patterns:** Broker→Lease→Receipt, Plan→Apply→Receipt

The removable-media local fallback has narrowed into a first coding lane: storage-only, session-scoped, quarantine-first, host-controlled read-only mount, disposable no-network jail, finite filesystem-family admission, inert mounted tree, physical root-pinned walk, one selected regular-file subject, capture-first into `/work`, verified capture committed into authoritative quarantine store before detach, later work restarted in a fresh worker with `/ingest` absent, one digest-bound launcher-preopened read-only preserved subject, one broker-collected declared derivative sink, capability mode before later tool mainline, closed-world reviewed descriptors, launcher-owned stdio, reviewed environment/argv/cwd, launcher-pinned executable identity, launcher-pinned runtime dependency closure, launcher-fixed unprivileged credentials, launcher-supervised daemon-free lifecycle, a launcher-enforced resource envelope, a launcher-isolated peer-interaction envelope, and a launcher-sealed ambient-input envelope.

This page closes the next network-egress seam:

> **the later worker must not let sockets, DNS/NSS/name-service lookup, proxy configuration, remote fetches, telemetry, license checks, update checks, safe-browsing lookups, or callbacks become unrecorded derivative inputs or exfiltration paths.**

See also:
- ADR: `adrs/ADR-0346-removable-media-local-fallback-post-detach-network-egress-stays-absent-and-receipt-visible.md`
- previous cut: `docs/756-removable-media-local-fallback-post-detach-ambient-inputs-stay-launcher-sealed-and-receipt-visible.md`
- network broker: `docs/281-network-egress-broker-and-consent.md`
- DNS mediation: `docs/305-dns-mediation-and-hostname-binding.md`

## Decision

For the first host-local removable-media fallback lane, post-detach later workers now use:

- `network-egress-absent-no-socket-dns-or-remote-callbacks`
- `receipt-records-network-absent-envelope`
- `no-dns-mdns-nss-or-resolver-host-input`
- `no-proxy-or-remote-service-configuration`
- `no-remote-fetch-or-callback-derivative-authority`

These strings do not require one specific kernel mechanism. They require that the ordinary derivative worker has no network socket egress, no resolver/name-service authority, no proxy configuration authority, no remote fetch/callback authority, and receipt-visible evidence that the no-network envelope was in force.

## Boundary rules

### 1) Network egress is absent, not merely discouraged

The later worker records `network-egress-absent-no-socket-dns-or-remote-callbacks`. No `AF_INET`, `AF_INET6`, raw socket, link-layer socket, DNS socket, proxy tunnel, remote scanner, update endpoint, license server, telemetry endpoint, safe-browsing service, or callback/reporting channel participates in ordinary derivative output.

A backend may implement this with jail networking disabled, network namespace isolation, Capsicum descriptor discipline, firewall rules, socket syscall filtering, or a combination. The portable contract is that network authority is absent in this first lane and must be explicit if admitted later.

### 2) Receipts expose the no-network envelope

The later worker records `receipt-records-network-absent-envelope`. A reviewer should not need to infer no-network behavior from host defaults, service names, or a remembered jail template. The plan, receipt, detach mapping, attach grant, and preopen map all carry the network posture that was enforced.

### 3) Name resolution is input authority and stays out

The later worker records `no-dns-mdns-nss-or-resolver-host-input`. DNS, mDNS, NSS, `/etc/hosts`, resolver configuration, directory-backed name service, and host search-domain behavior are all treated as possible input authority. They do not shape ordinary derivative output in the first lane.

This is separate from the ambient-input cut: even if time/random/host identity are sealed, name resolution can still introduce remote state, local policy state, and timing-dependent results.

### 4) Proxy and remote-service configuration stay out

The later worker records `no-proxy-or-remote-service-configuration` and `no-remote-fetch-or-callback-derivative-authority`. `HTTP_PROXY`, `HTTPS_PROXY`, `ALL_PROXY`, `NO_PROXY`, desktop proxy settings, PAC files, browser safe-browsing helpers, license checks, update pings, remote malware scanners, telemetry endpoints, and callback channels are not admitted into the post-detach worker.

If a future compatibility lane needs a remote scanner or reputation service, it must use the network egress broker, name the remote authority, bind the consent/lease, and receipt the request/response posture.

### 5) Canonical examples carry the posture

Canonical examples carry network-egress posture through:

- `post_detach_network_posture`
- `post_detach_network_receipt_posture`
- `post_detach_name_resolution_posture`
- `post_detach_proxy_posture`
- `post_detach_remote_dependency_posture`

The preopen map carries launcher-facing equivalents:

- `network_posture`
- `network_receipt_posture`
- `name_resolution_posture`
- `proxy_posture`
- `remote_dependency_posture`

Together with descriptors, launch context, executable and runtime closure identity, credentials, lifecycle, resources, peer interaction, and ambient inputs, these fields make the worker's remote-authority boundary reviewable without reading host-local network defaults.

## Canonical first-cut example stack

The network-egress cut is now explicit in:

- `spec/examples/device.attach.grant.removable-media-local-ingest.json`
- `spec/examples/content.import.plan.removable-media-local-ingest.json`
- `spec/examples/device.detach.receipt.removable-media-local-ingest.json`
- `spec/examples/content.import.receipt.removable-media-local-ingest.json`
- `spec/examples/preopen.map.removable-media-local-ingest-post-detach.json`

Together they now say:

- no socket/DNS/proxy/remote-callback authority is admitted,
- no DNS/NSS/resolver/default proxy state shapes derivative bytes,
- remote fetches, license checks, update pings, telemetry, and reputation-service lookups are out of the ordinary lane,
- and any compatibility lane that needs network authority must declare, broker, and receipt it explicitly.

## Why this cut is worth making now

Without this decision, the archive could produce receipts that look complete but still hide remote dependencies:

- identical preserved subjects could produce different derivatives based on DNS or remote service state,
- a sanitizer could fetch helper policy, reputation data, updates, or fonts over the network,
- proxy and resolver configuration could leak source metadata or subject-derived identifiers,
- license/update/telemetry callbacks could become exfiltration paths,
- and support could mistake a remembered no-network jail default for portable evidence.

This cut keeps the first lane boring: one preserved subject, one declared bounded derivative slot, one launcher-owned evidence path, no unrecorded remote authority.

## Compatibility impact

Some tools genuinely need remote reputation services, update feeds, license validation, DNS lookups, or proxy-mediated services. Those tools are not rejected forever; they require a future explicit compatibility lane that:

- declares the remote authority,
- binds it through the network egress broker and consent/lease surfaces,
- records name-resolution, proxy, and remote-dependency posture in receipts,
- preserves one-subject and derivative-egress invariants unless separately reviewed.

The current first lane remains network-absent and receipt-visible.

Last updated: 2026-05-18r502
