# Bounded range reconstruction construction and provider evidence — 2026-08-22

## Result

The default-off Agent now negotiates `state-sync-ranges-v1` and completes a signed successor pull
through one bounded missing-range bundle. The deterministic live-Agent fixture began with an accepted
generation-1 16,384-byte artifact, changed one contiguous 4,096-byte target region, fetched exactly
4,096 bytes, reused 12,288 bytes from the verified basis, reconstructed the exact generation-2
artifact, and accepted the linked HEAD last.

The subsequent genuine two-guest gate passed over direct UDP and forced TCP. Both cells pulled and
activated generation 1, then reconstructed an exact 4 MiB generation-2 successor through one
128-byte range while reusing 4,194,176 bytes. The retained proof and exact identities are in
`2026-08-22-sandwurm-sync-range.md`.

## Boundaries exercised

- confirmed IoTox HELLO negotiation with bits 18 and 26;
- exact authority-ledger v3 `sync.subscribe`/`sync.publish` proof;
- candidate signed-HEAD and accepted-parent verification;
- complete manifest transfer and semantic verification before planning;
- canonical one-range request bound to current HEAD and explicit FileId;
- mock c-toxcore paused offer, receive resume, chunks, and terminal callbacks;
- durable target-attempt journal before receive admission;
- private range-bundle shape/size checks and pathname unlink before reconstruction;
- complete SHA-256 verification, immutable-object commit, attempt clearance, scheduler commit, then
  accepted-HEAD advance;
- content-free `sync-status` evidence for range count, fetched bytes, and reused bytes.

## Verification

Four parallel GCC Debug shards passed all 519 owned unit/integration checks. The 16 runnable process,
restart, CLI, and lifecycle gates also passed. Five delegated-cgroup process cases skipped because no
delegated root was configured for this host run. Clang 21 Debug, Clang ASan/UBSan, and GCC Release
also passed all 519 checks. Both genuine Sandwurm cells and both independent compact-proof
reverifications passed.

## Nonclaims

The deterministic process fixture uses mock toxcore; the separate Sandwurm evidence closes the real
provider and two-route construction claim. Neither is a performance benchmark. Restart continuation
of a partially received range bundle, deterministic-directory convergence, multi-source scheduling,
destructive GC safety, and power-loss qualification on target storage remain open. Missing/corrupt
accepted-basis whole-successor recovery is now covered by ADR 0137 and genuine dual-carrier evidence;
corrupt target-object scrub remains open.
