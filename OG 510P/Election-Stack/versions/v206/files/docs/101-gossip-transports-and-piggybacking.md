# Gossip transports and piggybacking

**Track:** A (Deployable core)


## Why transports matter
If gossip relies on one channel (e.g., a single API), that channel becomes a censorship choke point.

Goal: ensure gossip can still spread when the *primary* evidence portal is unstable or selectively blocked.

## Transport menu (in increasing paranoia)

### A. Direct monitor-to-monitor gossip (baseline)
- HTTPS POST/GET between known monitors
- Signed payloads
- Rate-limited

### B. Witness mesh gossip
- Witnesses exchange digests as part of normal checkpoint signing
- Makes “witness capture” harder to hide

### C. Piggyback gossip (high leverage)
Attach checkpoint/bundle hashes to traffic that already flows:
- election status page updates
- voter receipt polling responses
- observer kit downloads
- (optional) unrelated high-volume channels where appropriate

This mirrors patterns used in key transparency deployments where log hashes are gossiped in-band.

### D. Out-of-band / side-channel gossip
- email lists to accredited observers (signed digests)
- RSS/Atom feeds with signed hashes
- physical notarization channels for final bundles (court filing, print publication)

## Normative requirements
- **MUST** support at least two independent transports.
- **SHOULD** ensure at least one transport is not reliant on the main evidence CDN.
- **MUST** sign gossip messages and include replay protection (nonce + timestamp window).

## Operational guidance
- Treat gossip endpoints as “public safety infrastructure”: monitor, rate-limit, publish uptime SLOs.