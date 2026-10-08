# Rev0996 audit — framed recovery and byte-locked release evidence

## Priority chosen

Rev0995 left two concrete trust-path risks rather than a shortage of doctrine:

1. a large recovery payload was copied through base64 and canonical JSON, then
   reread even when save already held the durable bytes; and
2. the reproducible-release lane still trusted mutable ambient builder packages
   and produced unsigned, runner-ephemeral evidence.

Rev0996 reproduced the first cost, removed it without a second recovery system,
and then finished the narrowest useful builder/provenance path. No database,
watcher, lock registry, package manager, background service, or new text engine
was introduced.

## Landing 1 — framed raw-tail recovery

### Severe and wasteful findings corrected

- A 16 MiB payload produced a 22,370,271-byte v1 record, about 72.7 MiB of
  additional traced checkpoint allocation, and about 95.1 MiB of traced load
  allocation.
- Immediate save reread and base64-decoded the checkpoint it had just durably
  written.
- Listing, inspection, residue discovery, mode repair, and restart-time commit
  materialized payload bytes even though they needed only verified authority.
- The first fast-commit witness was captured by pathname after publication; a
  replacement in that interval could inherit authority for the fsynced temp.

### Correction

- New writes use `micromax.recovery.v2`: fixed magic, four-byte big-endian header
  length, compact canonical JSON authority header, and exact raw payload tail.
- The default private atomic writer writes bounded parts directly; it does not
  join the complete record or base64-encode payload bytes.
- Header checksum, exact size, payload SHA-256, truncation, and trailing-byte
  checks fail closed.
- V1 JSON/base64 records remain readable and retire naturally; filenames retain
  the established `.recovery.json` lineage.
- Authority-only operations hash v2 payloads in bounded blocks. Only `load()` and
  `payload()` materialize recovery bytes.
- Immediate commit retains payload-free authority bound to the actual temporary
  inode that was fsynced and atomically published. Replacement invalidates or
  prevents the shortcut before any document write.
- Shared record validation serves legacy/full/authority reads, and candidate
  construction reuses the already-validated digest.

### Measurement

The permanent three-sample 16 MiB witness records:

- v2 record: 16,777,982 bytes, 24.999% smaller than v1;
- checkpoint traced peak: 19,561 bytes, down 99.973%;
- explicit load traced peak: 16,791,015 bytes, down 82.340%;
- verified authority inspection: 2,109,340-byte traced peak;
- restart-time commit: 2,109,386-byte traced peak; and
- same-instance checkpoint/commit: 2,106,468-byte traced peak.

`tracemalloc` begins after the immutable source exists and is not RSS, total
memory, native allocation, page cache, portable latency, or power-loss evidence.
Explicit load still necessarily returns one payload object. Legacy records and
an injected one-bytes writer callback retain historical full materialization.

### Integrity audit

A byte-identical replacement was injected after directory sync and after the
outer checkpoint write hook. Both races are rejected. The replacement remains a
valid record for ordinary parsing, but never receives the in-memory authority of
the fsynced inode. The witness is only an optimization: restart, signature drift,
or uncertainty falls back to complete bounded validation.

## Landing 2 — exact builder bytes and hosted provenance configuration

### Severe and incomplete findings corrected

- Rev0995 recorded builder version strings but did not authorize the bytes that
  supplied pip, setuptools, pytest, or their dependencies.
- Bootstrapping a locked pip through an older ambient pip would leave circular
  installer authority.
- Pull-request verification and hosted attestation were not separated by
  privilege.
- A configured attestation had no retained subjects after runner teardown.
- A fixed builder work directory poisoned a retry after an earlier attempt.
- Documentation used “offline” more broadly than the implemented pip boundary.

### Correction

- `release/requirements-builder.txt` locks seven exact wheel projects and SHA-256
  hashes under a deliberately narrow parser.
- The ambient interpreter may only download exact binary rows. Micromax then
  independently checks stable regular inodes, exact hashes, project/version
  metadata, path aliases, compression, encryption, file kinds, and resource
  ceilings.
- A pip-less virtual environment safely extracts the verified pip wheel, then
  installs the remaining verified wheelhouse with index resolution disabled,
  hashes all wheel bytes again, and checks the exact installed set.
- A self-digested builder receipt binds the source lock, exact wheels, installed
  versions, verifier ceilings, and network boundary to the release child.
- Package-policy audit consumes the executable `mxrelease` report instead of
  stale duplicate strings.
- Pull requests and ordinary pushes run with `contents: read`; only tag/manual
  runs receive OIDC, attestation, and artifact-metadata write authority.
- Checkout, setup-python, attest, and upload-artifact are pinned to full reviewed
  commits. The privileged job attests the wheel, receipts, and revision ZIP, then
  retains those exact explicit files for 30 days with missing-file failure and
  hidden-path handling.
- The ordinary Make target uses a fresh private builder tree. Final output still
  refuses overwrite.
- Receipts now say “pip index resolution disabled”; no OS network sandbox is
  claimed.

## Adjacent file-write test audit

The POSIX private-temp regression had accidentally required the portable named
`0666` mode-probe fallback to run before the `0600` payload temp. On Linux and
filesystems that support `O_TMPFILE`, the mode probe is deliberately unnamed, so
the instrumentation correctly observes only the `0600` payload inode. The test
now accepts either supported probe lane and asserts the real invariant: every
named inode that can receive document bytes is owner-only from creation. This
removes a baseline/environment false failure without weakening the production
privacy contract or adding another implementation branch.

## Evidence and qualification

The counted local evidence is deliberately split by owner:

- 95 builder, release, receipt, workflow, and archive-verifier tests;
- 47 framed-record and recovery-journey tests;
- eight interrupted-save/restart/normalization/aggregate-retirement cases run in
  individual focused invocations;
- 36 revision-index, documentation, context, structural-audit, and
  effect-contract tests; and
- the adjacent private-temp creation regression as one separate filesystem test.

That is 187 focused passing tests. A later combined interrupted-save invocation
exceeded its 15-minute supervisor after three visible completions and no observed
failure; it is not counted as a completed suite. The monolithic repository suite
was not run and is not claimed.

Compilation, repository lint, generated effect-contract checks, executable package
input audit, and revision context checks are green. `make timely` passed context,
audit, lint, 172/172 portability cases, and doctor preflight. Mypy is not installed
in this cloudtainer and the Make target reports that skip; it is not counted as a
passing typecheck. Archive construction and exact archive verification remain
final publication gates rather than evidence inferred from prose.

This cloudtainer provides Python 3.13.5 while the declared hosted lane requires
Python 3.13.14, and PyPI DNS resolution was unavailable during acquisition. The
builder correctly fails closed on the Python mismatch. Therefore no local
end-to-end builder receipt, GitHub-hosted execution, attestation, retained
workflow artifact, public release, or cross-platform result is claimed.

Format rationale, primary online sources, measurements, and residual risks are in
`docs/953-framed-raw-tail-recovery-audit.md` and
`docs/954-byte-locked-release-builder-hosted-provenance-audit.md`. The permanent
recovery measurement is `.artifacts/rev0996-framed-recovery-record.json`.
