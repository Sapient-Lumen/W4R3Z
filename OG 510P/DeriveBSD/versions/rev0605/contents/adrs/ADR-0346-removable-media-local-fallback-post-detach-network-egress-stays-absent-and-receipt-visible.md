# ADR-0346: Removable-media local fallback post-detach network egress stays absent and receipt-visible

- Status: accepted
- Date: 2026-05-18
- Deciders: archive maintainers
- Consulted: `docs/281-network-egress-broker-and-consent.md`, `docs/305-dns-mediation-and-hostname-binding.md`, `docs/756-removable-media-local-fallback-post-detach-ambient-inputs-stay-launcher-sealed-and-receipt-visible.md`, `spec/preopen.map.schema.json`

## Context

ADR-0337 through ADR-0345 made the post-detach removable-media later worker closed-world across descriptors, launch context, executable identity, runtime dependency closure, credentials, lifecycle, resources, peer interaction, and ambient host inputs. One remaining authority seam is network egress: a worker can still try remote fetches, DNS/NSS lookups, proxy discovery, update checks, telemetry, license validation, safe-browsing lookups, or callback/reporting channels and let those remote observations shape derivative bytes without those inputs appearing in the receipt.

The first removable-media local fallback is supposed to be a one-shot computation over one preserved subject and one declared derivative sink. Network effects are a separate brokered lease family elsewhere in the archive, not an ambient property of local ingest.

## Decision

For the first host-local removable-media fallback lane, post-detach later workers now use `network-egress-absent-no-socket-dns-or-remote-callbacks`, `receipt-records-network-absent-envelope`, `no-dns-mdns-nss-or-resolver-host-input`, `no-proxy-or-remote-service-configuration`, and `no-remote-fetch-or-callback-derivative-authority`.

These strings do not require one specific kernel primitive. They require that the ordinary first lane has no network socket egress, no resolver/name-service authority, no proxy configuration authority, no remote fetch/callback authority, and receipt-visible evidence that the no-network envelope was in force.

## Consequences

- The later worker cannot convert DNS, mDNS, NSS, resolver files, directory-backed name service, proxy settings, PAC files, remote scanners, license servers, telemetry endpoints, update checks, or safe-browsing callbacks into hidden derivative input authority.
- A tool that needs a remote service belongs in a later explicit compatibility lane that uses the existing network egress broker/consent surfaces and receipts the exact remote authority it consumes.
- Receipts become clearer: `network = none` is now backed by post-detach posture fields in the plan, import receipt, detach mapping, attach grant, and preopen map rather than relying on prose about a no-network jail.

## Alternatives considered

- **Rely on `execution.network = none`.** Rejected because it is too coarse; it does not name DNS/NSS/proxy/remote-callback authority or require receipt-visible enforcement.
- **Let tools perform benign lookups.** Rejected for the first lane; benign remote lookup is still an input, a timing channel, and an exfiltration surface unless brokered and receipted.
- **Model every remote service now.** Rejected as too broad. The ordinary lane stays network-absent, and compatibility lanes can be designed separately.

## Follow-up

- Update canonical removable-media local-ingest examples so they record network, name-resolution, proxy, and remote-dependency posture.
- Add a drift check that fails if the first lane slides back to socket/DNS/NSS/proxy/remote-callback authority or receipt-invisible no-network assumptions.

## Links

- boundary doc: `docs/757-removable-media-local-fallback-post-detach-network-egress-stays-absent-and-receipt-visible.md`
- previous cut: `adrs/ADR-0345-removable-media-local-fallback-post-detach-ambient-inputs-stay-launcher-sealed-and-receipt-visible.md`
