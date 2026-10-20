# ADR 0250: Bootstrap and accept complete content revisions

Status: accepted transport-neutral product prerequisite; Agent dispatch, activation, reachability,
and genuine-provider evidence remain open, 2026-08-29.

## Context

ADR 0249 let the product create and serve a complete content-v2 fabric, but a fresh subscriber could
not enter it: page and chunk membership is defined by the root manifest, while the receiver did not
yet possess that manifest. Treating the root as an artifact chunk would make its logical kind
ambiguous. Accepting HEAD before reconstructing the complete artifact would also invert IoTox's
existing signed-truth ordering.

The content scheduler, CTA1 restart journal, and finite-file manager have independent identities.
They require one explicit join. A file offer may also arrive before its result because Tox custom
packets and file callbacks are not one ordered stream.

## Decision

Complete the already frozen type-28/29 kind field with kind `3`, `root_manifest`. It is valid only at
logical index zero and names exactly the manifest digest and size in the signed HEAD. Frame sizes and
all other offsets remain unchanged. Sparse availability remains page/chunk-only.

Add a bounded one-source subscriber service. It:

1. requests a signed HEAD on the authority session and requires exact-v3 `sync.publish`, writer
   membership, and the proven writer principal;
2. reuses an exact local root or reserves and signs a CTA1 root attempt before returning its request;
3. retains an early exact-FileId offer paused until the matching canonical `offered` result arrives;
4. reserves a fresh CTA1 attempt before each scheduler assignment, persists its complete
   HEAD/object/FileId/source/carrier binding before receive admission, and requests only one object at
   a time;
5. commits root, pages, and chunks through verified-copy CAS admission, retiring CTA1 only after the
   immutable commit; and
6. reconstructs into an exact private workspace, commits the whole verified artifact into the same
   CAS, and advances stable-device-signed accepted HEAD last.

Exact artifact CAS permits a retry after a crash in the narrow post-artifact/pre-HEAD window without
reconstruction. Publication and reconstruction workspaces share one exact `local-<16 lowercase
hex>` primitive with separate class roots. Cleanup validates owner, mode, device, link shape, and
name and refuses foreign entries. The toxsync scheduler now returns staging pathnames without
creating their directories; IoTox CTA1 admission is the sole creator of private network staging.

Cancellation before receive effect clears CTA1 without starting a file. Cancellation or failure may
leave verified unreachable CAS, but never accepted HEAD. This first subscriber deliberately uses one
complete primary source and one object lane. It does not consume sparse availability, stripe sources,
activate, or mutate reachability/GC state.

## Qualification

The owned registry now has 656 checks. A real paged local publication is served through the real
content publisher service into the subscriber. The test delivers the root offer before its result,
proves the file remains paused, transfers the root, pages, and chunks through exact FileIds, rebuilds
the byte-identical artifact, leaves CTA1 empty, and observes accepted HEAD only after whole-artifact
CAS. A second test cancels an early offer with zero receive/cancel effects and rejects its delayed
result. Separate acceptance tests inject cancellation after artifact CAS but before HEAD and prove
exact retry and duplicate acceptance. Workspace tests prove exact cleanup and foreign-entry refusal.

## Consequences

- A fresh receiver can now derive every requested content object from one authenticated signed HEAD
  without a synthetic local manifest fixture.
- The whole artifact becomes the stable activation/read object; chunk/page CAS remains deduplicated
  transfer and reconstruction material.
- Attempt IDs are replay fences, not transfer counters. A scheduler window transition may burn an ID
  before reporting that the exhausted window has no assignment.
- Agent construction, dispatch, local control/status/cancel routing, explicit content activation,
  signed reachability/repair/GC integration, and genuine Sandwurm evidence remain required. Feature
  bit 29 stays dark until those product gates close.
