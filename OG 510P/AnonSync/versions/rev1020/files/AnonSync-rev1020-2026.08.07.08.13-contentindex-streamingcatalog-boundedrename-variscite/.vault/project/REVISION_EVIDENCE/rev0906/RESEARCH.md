# AnonSync rev0906 research record

Primary sources reviewed on 2026-07-26:

- SQLite release history for 3.53.4 and the published `sqlite3.c` SHA3-256:
  https://sqlite.org/changes.html
- SQLite 3.53.4 amalgamation download identity:
  https://sqlite.org/download.html
- Syncthing high-level synchronization, block, watcher, scan, and index model:
  https://docs.syncthing.net/users/syncing.html
- Syncthing synchronized filesystem semantics:
  https://docs.syncthing.net/users/faq.html
- Willow grouping entries, areas, and bounded areas of interest:
  https://willowprotocol.org/specs/grouping-entries/
- Noise Protocol Framework overview and identity-hiding/security caveats:
  https://noiseprotocol.org/ and https://noiseprotocol.org/noise.html
- Messaging Layer Security protocol, RFC 9420:
  https://www.rfc-editor.org/rfc/rfc9420.html

## Verified dependency observation

SQLite 3.53.4 was published on 2026-07-24. The official release history lists:

- `sqlite3.c` SHA3-256:
  `67f423e9ebbbdc473cbc4772c872ee6b89f31fde4ed0279a5c25d5f65c043a16`
- source ID:
  `2026-07-24 19:02:57 bf7c7f30031888f4e796e429ab3978879485813aaca6f641c7b33e4e09459bcc`

The official download page lists the 3.53.4 amalgamation ZIP SHA3-256 as:
`628a44cfe82c66aed1ccbbe85a562d2e33ebe64b3288981ed76285612227934e`.

The cloudtainer's permitted archive download bridge returned an unsupported-media
refusal even though the remote request was successful, while the shell network
path lacked DNS resolution. No archive bytes could be independently admitted and
hashed in the workspace. The bundled 3.53.3 tree is therefore unchanged. This is
a supply-chain boundary, not evidence that 3.53.4 is unsuitable.

## Comparisons

### Syncthing

Syncthing continuously combines filesystem notifications with periodic full
scans, computes block hashes, exchanges index information, derives a global
version, and writes through temporary files. AnonSync has stronger aspirations
around exact evidence authority and crash-auditable cutpoints, but it still lacks
that ordinary continuous product loop and broad filesystem semantics.

### Willow

Willow organizes entries by subspace, path, and timestamp. Areas of interest can
bound the newest entry count and total payload size. This suggests a useful shape
for future AnonSync interest negotiation: explicit authorized ranges plus
resource budgets. Importing Willow itself is not recommended without first
mapping its authority and privacy assumptions to AnonSync's evidence model.

### Noise

Noise offers handshake patterns with mutual/optional authentication,
identity-hiding properties, and forward secrecy. Its specification explicitly
notes that payload fields, traffic analysis, and IP metadata can still reveal
participants. This reinforces that changing TLS alone would not make AnonSync
anonymous; identity disclosure, interest privacy, and traffic/endpoint privacy
are separate layers.

### MLS

RFC 9420 provides asynchronous group key establishment with forward secrecy and
post-compromise security. MLS is not a file synchronization protocol. Its useful
lesson is architectural: membership and key epochs need a separate explicit
state machine if AnonSync grows beyond fixed pairwise credentials.

## Reasoned conclusions and speculation

1. The immutable evidence DAG and full-history reconstruction should remain a
   normative correctness oracle, while production speed comes from separately
   derived indexes and catalogs that are continuously checked against it.
2. The likely product architecture is a small correctness kernel plus a typed
   production scheduler, not a single monolith containing both proof and policy.
3. Peer synchronization should eventually negotiate bounded authorized
   interests, not disclose complete catalogs by default.
4. Oldest durable generation is appropriate for the observed local starvation;
   a mature scheduler should additionally prove explicit dependency readiness
   and use chronology only for fairness/tie-breaking.
5. Privacy should be decomposed into content confidentiality, key evolution,
   interest privacy, identity disclosure, and traffic/endpoint protection. No
   single transport substitution satisfies all five.
6. Dependency upgrades should remain isolated, byte-verifiable revisions because
   the project's private VFS and WAL authority make SQLite changes unusually
   consequential.
