# DOWNLOAD-INCOMPLETE-PROVENANCE-01 coherence/refactor — rev0023

## Refactor result

This pass deliberately **reduced** six candidate rows into one coherent audited-backlog packet.

```text
DOWNLOAD-INCOMPLETE-PROVENANCE-01:
  U-226 = canonical lead.
  U-230 = file-entry safety support.
  U-250 = concurrent-access / lock-failure support.
  U-253 = incomplete identity-key support; needs ingress constraints before elevation.
  U-222 = neighboring complete-file same-size provenance policy.
  U-249 = finalization race / retry robustness sibling.
```

## Why not split them into separate reports?

The rows are individually meaningful, but separately suggesting all of them would create a noisy and partly incoherent patch set. The same maintainer fix has to decide how Nicotine+ identifies a local partial download, when it is safe to resume, how local file entries are opened, and how finalization is retried or revalidated.

A fragmented fix could easily do the wrong thing, for example:

```text
- Add a no-follow open check but still trust stale same-size incomplete bytes.
- Fix the hash delimiter but still ignore lock failures.
- Reject all incomplete resume, breaking ordinary interrupted downloads.
- Add a final move retry but keep no provenance on whether the source incomplete file belongs to the current transfer.
```

## Compatibility constraints

Preserve:

```text
- ordinary interrupted-download resume;
- cross-filesystem final moves;
- filename conflict avoidance for normal completed downloads;
- user ability to recover manually moved/downloaded files;
- platform differences where no-follow or advisory locking behavior varies.
```

Change or clarify:

```text
- stale exact-size incomplete files should not silently become finished without provenance;
- partial bytes should not be trusted across identity/generation/provenance mismatch;
- lock failure should not continue as if resume were safe;
- incomplete identity should be structured, not raw concatenation;
- final destination should be revalidated at the move boundary.
```

## Separation from other families

Keep separate:

```text
U-123:
  duplicate peer transfer-token / stale timer / F-session orphaning.

U-69/U-107/U-198:
  transfer-size/opened-file/upload provenance.

U-251:
  upload EOF-before-advertised-size lifecycle.

U-269:
  completed upload socket/slot lifetime.

U-248:
  share-scan mtime cache provenance.
```

## Next family

The next queued target is **TRANSFER-CONTROL-PATH-BUDGET-01 / U-271 + U-274 + U-256**, with U-272 retained only as an alias of U-256. That lane is lower severity than the strict candidates, but it is coherent and should be easy to prove/prune without adding registry sprawl.
