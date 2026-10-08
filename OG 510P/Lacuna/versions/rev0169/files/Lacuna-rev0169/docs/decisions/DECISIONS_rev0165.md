# Decisions — rev0165

## D165-01 — use canaries as falsification controls, not attestations

**Decision.** Label clean status narrowly: no unexpected exact copies of the preregistered tokens occurred in scanned local artifacts.

**Why.** Memory erasure, semantic isolation, tool denial, and provider independence cannot be inferred from absence of one string.

## D165-02 — preregister two scopes per cell

**Decision.** Create one operator-only token and one filesystem-only token for every opaque cell before execution.

**Why.** Prompt/context contamination and unrelated-file inspection are different failure channels. One token cannot distinguish them.

## D165-03 — derive tokens deterministically from committed private custody

**Decision.** Use domain-separated SHA-256 material containing assignment seed, run ID, cell label, and scope.

**Why.** This fixes token selection before results without adding runtime randomness or a second secret store. The tokens remain unique, opaque, reproducible under private audit, and semantically inert.

## D165-04 — keep the filesystem token body out of the driver

**Decision.** The driver exposes only filesystem source path and token digest.

**Why.** A worker that only receives the driver should not know the filesystem token. Exact appearance then pressures actual file access or an equivalent parent leak.

## D165-05 — treat the scenario dispatch as a private coordinator driver

**Decision.** The complete v2 driver may be supplied to the one cell coordinator, including a persistent-context control, but must not be forwarded to nested role workers or raters.

**Why.** The coordinator needs the whole condition contract; role workers need least-context cards. Calling both objects “worker prompts” obscures the experimental boundary and makes weaker operators over-share.

## D165-06 — scan automatically before blind-packet creation

**Decision.** Final cell acceptance compiles the scan before publishing any rating packet.

**Why.** Optional/manual scans invite omission. Post-rating scans invite outcome-dependent retention. Pre-rating automatic custody keeps findings backstage while fixing them before evaluation.

## D165-07 — retain leak-detected conditions

**Decision.** A finding never automatically discards, redacts, repairs, or reruns a cell.

**Why.** Otherwise the control becomes a cherry-picking tool. Contamination is an outcome/covariate to report, not a license to resample.

## D165-08 — scan the complete retained cell tree, including cube state

**Decision.** Search the content and relative pathname of every retained single-link regular file beneath each preregistered cell, including `cube.json`, `lacuna.sqlite3`, SQLite sidecars, and cooperative lock files. Apply no basename, suffix, or subtree exemptions, and refuse unplanned immediate children under `cells/`.

**Why.** A structurally valid cube can still contain leaked private bytes. Kernel verification and canary absence are orthogonal claims. Generic suffix or subtree exclusions would create avoidable false negatives and unmapped artifacts; bounded complete-cell scanning is the more honest experimental boundary.

## D165-09 — use exact source allowlists

**Decision.** Source paths are part of the plan. A token is ignored only at those exact paths.

**Why.** A global exclusion by filename, directory, or file type could hide a real copy. A post hoc source list would be manipulable.

## D165-10 — fail closed on unsafe or changing trees

**Decision.** Refuse linked, nonregular, multi-linked, oversized, or unstable scan members; make recursive enumeration errors fatal; and preserve the prior manifest state.

**Why.** An experiment control must not follow paths outside authority, accept a moving target, or silently skip an unreadable subtree. Exact retry is safer than best-effort traversal.

## D165-11 — authenticate scans by rebuilding them

**Decision.** Do not trust cached status/counts or only the scan digest. Re-enumerate and recompute the current frozen artifact tree during scenario audit.

**Why.** Later unreferenced files can carry leaked bytes. The artifact must remain true, not merely historically well-formed.

## D165-12 — keep canary custody private until unblinding

**Decision.** Plans and scans remain private; blind packet v1 is unchanged.

**Why.** Ratings should reflect player-visible output, not knowledge that one condition leaked a marker.

## D165-13 — bind scans into replicated seals

**Decision.** Advance bundle block-seal/report contracts to v2 and include child scan custody.

**Why.** A replicated dataset must not lose the experimental-control result when moving from child reports to sealed blocks and aggregate export.

## D165-14 — separate exact matches from semantic judgments

**Decision.** The scan records byte-exact findings only. It does not ask a model to classify semantic leakage.

**Why.** Exact matching is deterministic, cheap, auditable, and can be preregistered. Semantic leakage evaluation is useful but belongs in a separately blinded external analysis.

## D165-15 — centralize the new boundary

**Decision.** Put canary policy and scanning in `contamination.py`; keep scenario and bundle modules responsible only for state transitions and joins.

**Why.** Secure recursive file handling is a reusable audit boundary and should not be duplicated across runners.

## Consequence for the next revision

The next evidence-bearing work should run live provider conformance with retained raw transports, explicit fresh-call settings, card-only workspaces, and canary results. A semantic leakage probe or worker-safe scenario prompt compiler may be added above this exact byte-level baseline; neither should widen story-kernel authority.
