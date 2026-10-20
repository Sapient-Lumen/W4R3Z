# ADR 0124: bind sync requests to explicit Tox file IDs

Status: accepted

Date: 2026-08-21

## Decision

Synchronization v1 uses IoTox lossless message types 20 through 23 for two bounded request/result
pairs: signed-HEAD discovery and immutable-object offer negotiation. Feature bit 18
(`state-sync-v1`) remains default-off and unadvertised until the Agent installs the complete
authorization and replay dispatcher.

Every object request names the namespace, immutable object kind, digest of the exact complete signed
HEAD record, and one nonzero 32-byte transfer token. The publisher must pass that token as the
explicit c-toxcore FileId when it offers the corresponding final digest-named object. The subscriber
matches a paused incoming offer by exact FileId and obtains expected kind, digest, and byte count from
the already verified signed HEAD. A remote filename is presentation data and never selects an object,
destination, namespace, or attempt.

The generic file-transfer manager now has a narrow explicit-FileId send entrance. It reads the ID
back from c-toxcore and cancels the offer if the provider changed it. The auxiliary-worker supervisor
exposes that entrance only for an exact reciprocally authenticated bulk worker incarnation. It
preallocates outgoing-attempt records before transport startup and shares the existing non-evicting
terminal-event budget between sends and receives. Completion, cancellation, failure, peer loss, and
trust loss therefore retain exact route/worker/file/FileId truth in either direction.

HEAD and object requests have a nonzero message ID and zero correlation, sequence, expiry, and flags.
Results have an independent nonzero message ID and the request ID as nonzero correlation. Exact
payload layouts and status values are frozen in `protocol-sync-wire-v1.md`. Duplicate and stale
classification is scoped to the confirmed online session by the future dispatcher; the records alone
carry no ambient authority.

## Consequences

The signed request and later Tox file offer now have a collision-resistant application-chosen join
that survives arbitrary filenames and opaque provider file numbers. A transfer offer or `offered`
result still proves neither completion nor content correctness: only staged size/digest verification,
exclusive object commit, and the durable attempt protocol can complete an object.

The wire codec deliberately does not advertise the feature, dispatch traffic, grant namespace
access, accept HEADs, activate revisions, or persist request replay. Agent integration must combine
the exact current authority proof, namespace membership, confirmed-session epoch, request replay
state, and worker binding before either a HEAD disclosure or file offer effect. FileId secrecy is not
assumed; uniqueness and exact correlation are the properties used.
