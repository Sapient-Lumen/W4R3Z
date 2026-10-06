# ADR-0170: Publish-session local-service URI hints stay loopback-shaped

- Status: Accepted
- Date: 2026-03-19

## Context

ADR-0152 fixed the high-level `net.publish.session` boundary by keeping the **source service local-first** and pushing outward publication onto an explicit relay-backed lane.
ADR-0165 through ADR-0169 then progressively made the outward endpoint and relay fields coherent.

That still left one smaller ambiguity on the **local-source** side:

**if `local_service.service_uri_hint` is present, what stops it from pointing at a LAN/public target, or from carrying secret-bearing localhost text that contradicts the local-first boundary?**

Without one more narrow decision, a publish-session receipt can say the source is `loopback-only` while its copied service hint quietly names a non-loopback host, embeds userinfo, or hides query/fragment material that support bundles and CLI output were never meant to treat as credentials.

DeriveBSD does not need a richer local-endpoint object yet, but it does need one coherent rule for how the optional human/debugging hint on the local side relates to the already-decided local-first source boundary.

## Decision

1. `local_service.service_uri_hint` remains optional.

2. If present, it must be an **absolute URI-shaped hint with authority**.

3. If present, its authority host must stay **loopback-shaped**:
   - `localhost` or any name under `.localhost`, or
   - an IP loopback literal such as `127.0.0.1` or `::1`.

4. If present, it must stay **secret-clean**:
   - no userinfo,
   - no query,
   - no fragment.

5. For obvious scheme-bearing protocols, the URI scheme must follow `local_service.protocol`:
   - `protocol = http` ⇒ `service_uri_hint` uses `http://`
   - `protocol = https` ⇒ `service_uri_hint` uses `https://`
   - `protocol = ssh` ⇒ `service_uri_hint` uses `ssh://`

6. This ADR still does not standardize richer typed local endpoint objects, Unix-socket publication, gRPC sub-taxonomy, or adapter-specific health-check URLs.

## Consequences

- The source side of a publish session now tells the same local-first story as the rest of the receipt.
- Support/UI/export surfaces can safely show `service_uri_hint` as a local debugging hint instead of wondering whether it is actually a second outward endpoint or a credential-bearing localhost string.
- The archive gets a tighter forensics/operability floor without front-loading a larger local-endpoint subsystem.

## Alternatives considered

- **Leave `service_uri_hint` free-form.** Rejected because that would leave the local side as the next cheap ambiguity after the archive already paid to make the outward side coherent.
- **Delete `service_uri_hint` entirely.** Rejected for now; local debugging/support still benefits from a human-readable local endpoint hint, but that hint must stay subordinate to the local-first boundary.
- **Design a richer typed local-endpoint object now.** Rejected as premature.
