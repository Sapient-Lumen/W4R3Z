# Rev0875 research notes

Primary and official sources consulted:

- Linux time namespaces require optional `CONFIG_TIME_NS` and do not virtualize
  `CLOCK_REALTIME`: https://man7.org/linux/man-pages/man7/time_namespaces.7.html
- `CLOCK_BOOTTIME` includes suspend: https://man7.org/linux/man-pages/man2/clock_getres.2.html
- successful SQLite `BEGIN IMMEDIATE` starts a write transaction and excludes
  other writers: https://sqlite.org/isolation.html
- Noise provides DH handshake patterns, encrypted transport states, and a
  handshake hash suitable for channel binding: https://noiseprotocol.org/noise.html
- Syncthing documents TLS/device pinning and the metadata visible to observers and
  relays: https://docs.syncthing.net/users/security.html
- Syncthing's untrusted-device protocol uses two-phase metadata/block transfer and
  encrypted metadata: https://docs.syncthing.net/specs/untrusted.html
- MLS supplies continuous group authenticated key exchange while leaving delivery
  denial/loss handling to the application: https://datatracker.ietf.org/doc/rfc9420/
- NTS adds authenticated NTP exchanges after TLS-based key exchange:
  https://www.internetsociety.org/blog/2020/10/nts-rfc-published-new-standard-to-ensure-secure-time-on-the-internet/
- SLSA recommends isolated builders, trusted-control-plane signed provenance, and
  transitive-input cache binding: https://slsa.dev/spec/v1.2/threats

Interpretation and speculation are separated in the full audit. None of these
sources proves AnonSync's implementation correct.
