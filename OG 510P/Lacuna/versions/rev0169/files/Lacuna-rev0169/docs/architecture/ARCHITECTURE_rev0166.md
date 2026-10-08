# Architecture — rev0166

## Purpose

Revision 0166 is the send-oriented integration revision. It joins four previously separable concerns without widening story authority:

1. a player, a researcher, and an operator each receive a distinct top-level entrance;
2. an extracted release can audit its own manifest, member set, version identity, syntax, parseability, and local links without modifying the release;
3. a fresh post-checkpoint narrator can distinguish an explicit possibly partial public-history list from a checkpoint-bound complete census of durable pre-checkpoint audience turns; and
4. preregistered contamination canaries are searched across the complete retained cell tree, including cube files and pathnames, through one incremental authenticated content pass.

The database remains schema 8 and immutable event envelopes remain schema 1. Public-history/continuation and artifact-audit additions are exchange or host-side contracts; they add no model client, story truth layer, automatic trigger, aesthetic authority, or provider attestation.

## Three-door release surface

```text
PLAY_NOW.md       player: say “Will you DM?” and play
FOR_GWERN.md      researcher: implemented claim, nonclaims, shortest appraisal path
OPERATE_LACUNA.md parent/operator: capabilities, commands, recovery, context isolation
```

`START_HERE.md`, `README.md`, and `docs/README.md` route to these entrances before long reference material. `tests/test_release_surface.py` treats their presence, manifest membership, route order, and final revision identity as release invariants.

The entrance split is deliberately not a new authority system. A player never receives checkpoint or filesystem duties. A researcher is not told that passing custody proves efficacy. An operator still follows `run.json`/`NEXT.md`, and only the parent may accept, review, recover, commit, seal, unblind, or present receipt narration.

## Extracted-artifact audit

`lacuna artifact check` emits `lacuna.artifact-audit.v1`. It checks one extracted release root for:

- valid and unique `MANIFEST.sha256` entries;
- safe regular members and exact SHA-256 agreement;
- missing members and, under `--strict-members`, every unlisted regular file;
- runtime, `pyproject.toml`, source, `REVISION.json`, and root-directory version coherence;
- Python syntax;
- JSON and TOML parsing; and
- relative Markdown link resolution.

The launcher starts Python with `-S` and `PYTHONDONTWRITEBYTECODE=1`, so a read-only check does not create `__pycache__` members that would make a pristine extraction fail strict membership later.

This command is release-adjacent custody, not story mutation. It does not build ZIP files, verify a distributor identity, provide a trusted timestamp, or make a replaced archive/verifier pair trustworthy.

## Complete public-history custody

Rev0166 retains the v2 public-history branch and makes its denominator explicit.

### Explicit list

`history build RUN...` emits `lacuna.public-history.v2` with:

```text
coverage.mode = explicit-run-list
coverage.completeness = not-claimed
```

Every included committed managed turn is authenticated against its request, exact player input, proposal, narration source, receipt, cube identity, audience, and immutable event position. The list may still omit earlier public turns.

### Checkpoint-bound census

`history complete CHECKPOINT_RUN --run-root ROOT...` derives the expected turn set from durable ledger custody before the authenticated checkpoint request, then requires exactly one retained committed managed run for each expected request/proposal pair. It emits:

```text
coverage.mode = complete-before-checkpoint
coverage.completeness = complete
```

The command refuses missing or duplicate runs, direct/stateless committed turns whose transcript sidecar is unavailable, wrong cube/audience/boundary/version/path, chronology overlap, or any run/ledger disagreement. A zero-turn census is valid and needs no dummy run root.

Completeness is deliberately bounded. It covers durable Lacuna play-purpose turns for one audience before one checkpoint. It cannot census uncommitted external chat or reconstruct transcript bodies that were never retained.

## Continuation dispatch v2

`lacuna.checkpoint-continuation-dispatch.v2` joins one authenticated committed checkpoint to one exact fresh, audience-only, solo, no-anchor ordinary turn. It declares exactly one public-context mode:

```text
typed-only
bound-public-history
complete-bound-public-history
```

The fresh narrator receives typed audience custody, selected compressed planning state, exact next player input, and—when supplied—only `lacuna.public-history-view.v2`, which strips parent-side run IDs, proposal IDs, receipt hashes, and event positions. Rejected candidates, rollouts, scores, verifier findings, provider provenance, and parent orchestration history remain excluded.

The dispatch grants no accept or commit power. The returned object is still an untrusted `lacuna.turn-proposal.v2` until the ordinary turn run validates, prepares, and commits it.

## Complete retained-tree contamination scan

The scenario plan preregisters two opaque exact tokens per cell: one operator-only and one filesystem-only. After all four cells are frozen and before blind rating, `lacuna.scenario-contamination-scan.v1` covers:

- every retained regular-file body beneath the exact planned `cells/<opaque-label>/` trees;
- every normalized relative regular-file pathname;
- cloned cube databases;
- SQLite `-wal`, `-shm`, and `-journal` sidecars when present;
- cooperative lock files; and
- all other retained regular members, regardless of basename or suffix.

There is no cube-subtree, database-suffix, lock-name, or “known binary” content exemption. Verification of a cube and search of its bytes answer different questions.

The compiler fails closed on unplanned cell directories, traversal errors or skipped subtrees, symlinks, hard links, nonregular members, oversized/changing files, path substitution, limit exhaustion, or a changed second enumeration. Findings are classified as same-cell or cross-cell and content or relative-path matches. A detected cell is retained rather than silently rerun.

## Incremental authenticated scanner

`src/lacuna/sidecars.py` now centralizes the descriptor boundary used by both bounded reads and contamination scans:

```text
open no-follow descriptor
  → authenticate regular/single-link identity and size
  → stream bounded chunks
  → update SHA-256 and exact-token counts
  → retain max-token-length overlap between chunks
  → reauthenticate descriptor/path/metadata after EOF
```

The overlap logic counts a token split across read boundaries exactly once. This avoids loading a large SQLite file wholesale while preserving the same fail-closed link, identity, size, and change checks as other sidecar reads.

## Retained system shape

All earlier foundations remain:

- source-bound ordinary turns and managed checkpoints;
- generator → provenance-stripped judge → winner-only compressor → verifier checkpoint topology;
- exact rollback preparation and current/historical commit recovery;
- fresh-narrator role definitions for portable, Codex, Claude Code, Gemini CLI, and ChatGPT transports;
- four fixed comparative conditions and replicated all-blocks-before-any-unblind bundle custody;
- deterministic blind-rating and rater-level export contracts;
- commitment, consequence, seal, particle, visibility, and unknown-state distinctions; and
- parent-only acceptance and durable mutation authority.

## Nonclaims

A passing artifact audit proves local agreement under the supplied verifier, not authorship or trusted distribution. A complete public-history artifact proves its bounded durable-turn census, not all conversation history. A clean exact-token scan means only that the preregistered strings were absent from the retained scanned content/path scope. None of these proves provider memory erasure, hard tool denial, semantic noninterference, narrative quality, or that retcon planning causes better fiction.
