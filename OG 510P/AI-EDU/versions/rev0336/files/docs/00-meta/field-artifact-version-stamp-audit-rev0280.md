# Field artifact version-stamp audit rev0280

## Scope

This audit covers the scratch-local artifacts that are closest to real FT-0181
field progress: field-next dockets and owner-request packet manifests. It does
not audit historical release examples, schema versions, or branch surfaces whose
older revision names are part of archive history.

## Finding

Two live execution artifacts carried stale hard-coded version stamps:

| Artifact | Previous stamp | Risk |
|---|---:|---|
| `field-next-action.json` | `decision_version: rev0278` | The one-action router could look older than the release that generated it. |
| `packet-manifest.json` | `packet_version: rev0275` | The first-contact packet could look like an old packet even when freshly generated. |

The packet generator also contained a duplicate `evidence_state` key in the
source dictionary. JSON output kept only one value, so the emitted manifest was
not ambiguous, but the source code was still a maintenance smell in the highest
leverage lane.

## Repair

The packet and field-next tools now read the current release revision from
`REVISION_RECEIPT.json`. Their validators now enforce that current-revision
stamp. This keeps scratch-local execution aids semantically fresh without making
them evidence, acceptance, custody, closure, or public-claim support.

## Boundary

A current version stamp only proves that the local aid came from the current
release. It does not prove that the owner was contacted, that a packet returned,
that source truth is SRC2+, that a service changed safely, or that any public
claim is allowed.

## Next audit target

After a real owner packet arrives, audit only the artifact class the packet
actually touches. Until then, do not audit the rest of the control plane just
because it exists.
