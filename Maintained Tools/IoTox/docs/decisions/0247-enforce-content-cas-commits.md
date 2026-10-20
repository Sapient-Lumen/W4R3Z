# ADR 0247: Enforce content CAS commits

Status: accepted construction prerequisite; durable Agent attempts and genuine-provider evidence
remain open, 2026-08-29.

## Context

ADR 0246 made physical content storage visible to one namespace quota, but observation alone did not
stop a writer from bypassing the combined allowance. The transport-neutral coordinator also accepted
arbitrary local store/staging roots and exposed toxsync's `source_preverified` fast path. Those are
useful component seams, but they are not safe product defaults for peer-delivered bytes.

## Decision

Give every IoTox content-v2 namespace exactly two derived roots:
`ROOT/content-v2` for the canonical CAS and `ROOT/staging/content-v2` for incomplete bytes. Both are
owner-private and prepared only under the namespace transaction. A coordinator refuses any other
store or staging root, and a completion path must equal the scheduler's exact derived staging path.

Before immutable publication, the product commit path:

1. requires a nonzero digest, nonzero bounded size, and a normalized path beneath the canonical
   content staging root;
2. requires one mode-0600, owner-owned, single-link regular staging file on the namespace filesystem
   with the exact expected size;
3. scans flat plus CAS physical inventory under the same namespace transaction and prospectively
   charges one object and its bytes unless the exact destination already exists;
4. streams the source through SHA-256 into a no-replace CAS temporary, publishes only matching bytes,
   and consumes staging only after success; and
5. verifies an existing destination and the new source before treating exact retry as reuse.

The product path does not accept `source_preverified` and disables hard-link ingest. An extra copy is
preferable to a mutation interval between hashing a pathname and linking it into immutable truth.
Quota refusal happens before publication and leaves the active assignment plus staging file intact
for an explicit retry. Structural staging refusal likewise has no storage effect; the caller must
classify/fail or repair the retained attempt explicitly.

## Qualification

The owned registry now has 638 checks. Deterministic tests prove canonical root enforcement; root
manifest publication through the product commit path; verified copy, source consumption, exact
reuse, corrupt-source refusal, and strict inventory; coordinator page/chunk commits through combined
quota admission; quota refusal with no destination and retained retry state; and rejection of a
substituted completion path or hard-linked staging file.

## Consequences

- Content-v2 no longer has a construction-level quota bypass through its coordinator or public local
  staging commit primitive.
- The root manifest can enter the same CAS before coordinator construction without a parallel trust
  root. Durable live code must still bind that commit to its exact signed attempt and HEAD.
- This does not provide durable attempt/FileId/event joining, restart recovery, accepted-HEAD-last
  publication, authenticated reachability/repair/quarantine, or Agent dispatch. Bit 29 remains dark.
