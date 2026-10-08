# Session deep audit — rev0306

Focus: substance-preserving prose compression after actor-accountability and cube-axis hardening.

## What was risky

Rev0293 through Rev0301 made accountability profiles concrete, and Rev0302 through Rev0305 made live cube axes more queryable. The remaining risk was a different kind of waste: many route memos still carried full accountability tables even though the authoritative assignments were now in JSON profiles and checked by audits.

## What changed

Rev0306 rewrites 85 legacy accountability-map sections into compact accountability capsules. Each capsule still names the route profile, duty owner, rent/benefit trace, bottleneck/evidence start, and fallback duty, but it avoids repeating the full six-row table and boilerplate.

## Audit/refactor performed

Added `tools/audit_prose_bloat.py`, wired it into `make audit`, and made `tools/check_archive.py` run it. The audit now fails if legacy accountability-map headings, table headers, or boilerplate return.

## Remaining risk

The next risky bloat surface is not the capsule layer but long pre-existing calibration memos whose stage ladders, anti-patterns, and change-trigger sections may repeat across families. That should be handled by family-specific pruning rather than a broad string rewrite.
