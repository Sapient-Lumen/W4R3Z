# Operating surface protocol

## Purpose
Use this protocol when the repo is not merely asking **which contributions rank highest**, but **what common operating surface the strongest contributions should expose so the archive composes as a family in theory and in practice**.

This protocol exists to keep future revisions from inventing a new command grammar, receipt vocabulary, and negative-state style for every seam.

Read with:
- `design/epic-contribution-operating-surface-2026Q1.md`
- `design/epic-contribution-worthy-repo-buildout-2026Q1.md`
- `design/epic-contribution-live-ecosystem-refresh-2026Q1.md`
- `meta/WORTHY_REPO_BUILDOUT_PROTOCOL.md`
- `meta/LIVE_ECOSYSTEM_REFRESH_PROTOCOL.md`
- `meta/LLM_ARCHIVE_CONTINUITY_PROTOCOL.md`
- `meta/AMNESIA_RESISTORS.md`

## Required moves
1. Re-open the current canon before adding a new “shared surface” claim.
   - start from the latest buildout note, live-refresh note, packets, dossiers, and the strongest execution blueprints.
   - do not infer a family surface from one fresh tool or post.

2. Prefer primary sources that actually change operator surfaces.
   Prioritize sources that affect:
   - import or metadata surfaces;
   - command/report patterns;
   - service truth exposure;
   - machine-readable formats;
   - renewal/review expectations;
   - decision-rights or residency boundaries.

3. For every seam discussed, write five things explicitly.
   - the operator verbs it most needs;
   - the artifact roles it should emit;
   - the import surfaces it depends on;
   - the negative states it must report honestly;
   - the likely residency shape (companion, service-side, toolchain-distributed optional component, etc.).

4. Keep verbs separate from artifacts.
   - verbs are actions like `report`, `diff`, `review`, `waive`, `replay`, `renew`.
   - artifacts are outputs like session packs, review receipts, tuple cards, readiness packs, stale receipts.
   - do not let filenames or schemas masquerade as the operating grammar.

5. Keep operating surface separate from decision rights.
   - a shared operator grammar does not imply a shared upstream owner.
   - a toolchain-distributed optional component is not the same thing as Cargo core.
   - a service-side fact source is not the same thing as a boundary-review product.

6. Default to companion-first families before hosted-platform fantasies.
   - prefer local or CI-attachable receipts, packs, and compare outputs.
   - only escalate to hosted aggregation when renewal and stewardship economics are actually credible.

7. Force negative-state receipts early.
   Every serious surface should have explicit posture for at least:
   - unsupported
   - stale
   - unknown
   - experimental
   - waived / exception granted
   - route-specific or partially trusted

8. Update continuity rails in the same revision.
   If the family grammar changed, refresh at least:
   - `AGENTS.md`
   - `INDEX.md`
   - `PRIORITIES.md`
   - `STRATEGIC_FRONTIER.md`
   - `RESEARCH_LOG.md`
   - `meta/ACTIVE_FRONTIER.md`
   - `meta/CANONICAL_WORKING_SET.md`
   - `meta/LATEST_REVISION_FILESET.md`
   - `meta/LLM_ARCHIVE_CONTINUITY_PROTOCOL.md`
   - `meta/REVISION_OPERATING_PROTOCOL.md`
   - `meta/AMNESIA_RESISTORS.md`
   - `atlases/portfolio-source-atlas-v0/sources.json`

## Default interpretation rules
- do not create a new top-band seam merely because a shared verb family became visible;
- do not let one current Cargo subcommand or one service API pretend to define the whole archive’s grammar;
- do not let shared schemas substitute for shared operator verbs;
- do not let the desire for a “clean framework” erase route-specific or negative-state truth;
- and do not ship assistant-facing synthesis that cannot say what is imported, what is emitted, what is compared, and how uncertainty is preserved.

## Failure modes
### Failure mode 1: every seam gets its own private grammar
This makes the repo look larger while making implementations less related and less stewardable.

### Failure mode 2: one source becomes a fake universal operating system
A Cargo prototype, a docs.rs surface, or a crates.io API can be a strong clue without defining every seam.

### Failure mode 3: verbs, artifacts, and ownership collapse together
`report` is not a schema, a receipt is not an owner, and a service API is not a governance product.

### Failure mode 4: hosted-control-plane drift
If a revision starts assuming a central hosted service before the local receipt and export grammar is mature, treat it as premature.

### Failure mode 5: assistant smoothing without receipts
If a revision describes a “great ecosystem platform” but cannot list the verbs, receipts, and negative-state posture, it is not archive-worthy yet.

## Preferred output shape for future revisions
When adding a new operating-surface refinement, prefer sections in this order:
1. what changed in the external signal;
2. what shared verbs became clearer;
3. what artifact roles should repeat;
4. what negative states must be standardized;
5. what residency shape is actually credible now;
6. which existing seams gain the most from the shared grammar;
7. what wrong shape should be refused.
