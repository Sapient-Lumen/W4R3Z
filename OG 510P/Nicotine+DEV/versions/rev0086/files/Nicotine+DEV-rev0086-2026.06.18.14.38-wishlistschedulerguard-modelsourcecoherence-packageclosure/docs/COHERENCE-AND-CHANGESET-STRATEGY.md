# Coherence and changeset strategy

This cube now treats fix composability as a first-class audit dimension.

## Why this matters

A finding can be individually true but still be a poor standalone recommendation. The peer/request-binding group is the first clear example: token generation, direct PeerInit replacement, secondary connection promotion, server-provided addresses, and upload/download transfer state all overlap. Fixing one in isolation can leave the same bug class reachable through another path, or break protocol compatibility.

## Coherence rules added in rev0006

1. **Prefer canonical families over isolated rows** when multiple rows share the same state boundary.
2. **Check protocol field availability** before recommending a binding rule. For example, UploadFailed and UploadDenied do not carry transfer tokens, so a token-required fix for those messages would be incoherent.
3. **Separate compatibility behavior from security acceptance.** Nicotine+ currently preserves some secondary/direct-indirect behavior for compatibility. A fix should make that transition explicit rather than blindly closing or blindly promoting.
4. **Do not treat upstream partial fixes as novelty.** Master’s allowed-response gate changes U-217 from “fresh no-gate finding” into a residual generation-binding audit item.
5. **Use one generation/provenance object where possible.** Repeated dictionaries keyed by username/path/token should be audited for shared lifecycle and collision behavior.

## Families created in rev0006

See `data/rev0006_coherence_map.csv` for machine-readable details.

- **PB-01 peer connection identity/generation binding**: U-168, U-176, U-165, U-171, U-181, U-169/U-170 as backreferences.
- **TR-01 transfer lifecycle provenance**: U-123, U-158, U-166, U-169, U-185, U-269.
- **PR-01 allowed heavy-response/request-generation gating**: U-217 plus parser/response-gating findings queued for later.
- **SRC-01 server-supplied address policy**: U-145, U-171, U-205.

## Known non-composable fix traps

- “Close every secondary connection” may break compatibility with peers that complete direct and indirect connection attempts in a race.
- “Require UploadDenied/UploadFailed tokens” is impossible without protocol changes because those messages do not carry tokens.
- “Bind ConnectToPeer to cached address exactly” may break NAT or stale-address recovery.
- “Make PierceFireWall token random” helps but does not solve source/generation binding or direct PeerInit replacement.
- “Gate UserInfoResponse by username” is a useful master change but may not be sufficient for request-generation or socket-level binding.
