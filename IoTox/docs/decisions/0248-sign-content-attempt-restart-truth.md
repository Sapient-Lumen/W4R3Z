# ADR 0248: Sign content-v2 attempt restart truth

Status: accepted construction prerequisite; Agent dispatch and genuine-provider evidence remain open,
2026-08-29.

## Context

ADR 0247 made each content CAS commit structurally and cryptographically safe, but a daemon restart
still lost the reason that one staging pathname existed. Guessing from digest/request filenames could
join bytes to a new HEAD, source, carrier, or FileId. Reusing the range-oriented `ATM1` record would
also erase the different content-v2 unit: one independently scheduled page or chunk among several
sources.

## Decision

Define the canonical `CTA1` journal in `sync-content-attempt-journal-v1.md`. Before transport effect,
each active record binds a burned attempt ID to the exact frozen signed-HEAD record, kind and logical
index, object digest and size, request/source IDs, FileId, complete carrier incarnation, and stable
source principal. The stable device signs every bounded canonical mutation and links it to the digest
of the previous complete signed state. Active request IDs, FileIds, and logical objects cannot alias.

Startup never revives a carrier. It loads the journal under the namespace transaction, verifies the
complete CAS, and may commit only an exact-size private staging object through ADR 0247's verified-copy
and prospective combined-quota entrance. Existing exact CAS truth is reused. Partial or absent staging
is fenced for a future fresh authorized request. Unsafe or corrupt-complete staging is ambiguous and
fails closed without retiring the record. Only after every active record has a safe classification is
the active set cleared in a new signed mutation.

The chain is detection evidence within retained current state, not a monotonic anti-rollback oracle.
The Agent must reapply current authority and HEAD admission before issuing any replacement request;
recovery itself grants neither remote reachability nor activation.

## Qualification

The owned registry now has 643 checks. Deterministic tests freeze the exact 192-byte header and
288-byte record encoding; signed-field and reserved-byte rejection; burned IDs; exact duplicate
idempotence; ID, request, FileId, and logical alias refusal; active bounds; canonical staging-name
derivation; complete-object recovery; partial/absent fencing; idempotent replay; journal tamper
rejection; and hard-link ambiguity retention.

## Consequences

- A content-v2 staging file now has durable signed meaning across daemon restart instead of merely a
  plausible name.
- A crash between individual object publication and journal retirement is safe to replay because
  verified CAS truth wins and the signed record remains until the final mutation.
- Partial content objects deliberately do not resume yet. Fresh authorized requests may replace them;
  byte-range continuation is a later optimization, not implicit recovery behavior.
- Agent request/result/file-event joining, authenticated reachability/repair/quarantine, accepted-
  HEAD-last publication, explicit activation, and genuine Sandwurm evidence remain required. Bit 29
  stays dark.

## Later qualification

ADRs 0251 and 0252 later qualified Agent dispatch and genuine native carriers. ADR 0267 adds the
unclean multi-lane restart gate at explicit caps two and four. That work discovered c-toxcore's exact
private pre-rename transport temporaries below the canonical `CTA1` pathname; startup now validates
and removes only that strict residue after loading signed attempt truth, preserves the complete CAS
inventory exactly, and requires a distinct two-sided-authorized pull. The 2026-08-29 status above is
the historical boundary of this decision, not the current product claim.
