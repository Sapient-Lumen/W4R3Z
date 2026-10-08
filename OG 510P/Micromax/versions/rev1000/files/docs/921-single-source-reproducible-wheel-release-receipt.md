# Single-source reproducible wheel and release receipt

Rev0965 closes the largest remaining release-truth gap: tests, package builds,
installed-runtime proof, and revision archives now derive from one captured set
of source bytes instead of repeatedly observing a mutable working tree.

## Why this work came first

Micromax already had careful archive lineage and verification, but the release
claim stopped at the archive boundary. Focused tests could observe one working
state, two wheel builds could observe later states, and the archive could capture
yet another. A correct manifest over the final ZIP did not prove that the tested
bytes were the packaged bytes. That was a higher trust risk than adding another
editor feature or registry.

The packaging audit also found two concrete defects:

1. Modern setuptools failed while creating the wheel because legacy license
   metadata and a manual `share/micromax/LICENSE` data-file collided with the
   PEP 639 `.dist-info/licenses` location.
2. Identical source payloads materialized with modes 0644 and 0600 built wheels
   with different SHA-256 digests. Forty-nine wheel members had the same bytes
   but different ZIP external attributes, chiefly installed documentation. The
   caller's umask had become an undeclared package input.

Rev0965 corrects both defects in executable code rather than adding a release
checklist that can drift from the build.

## One captured generation

`tools/mxrepro.py` is the narrow release lane. Its source flow is:

```text
verified live tree
    -> capture declared regular-file bytes once
    -> generate and validate MICROMAX-CONTEXT.json once
    -> seal source descriptor and digest
    -> materialize independent test, wheel-A, wheel-B,
       archive-A, and archive-B workspaces
```

The capture refuses unsafe paths, symlinks, non-regular members, duplicate
members, and source drift while bytes are being read. Before publication it
rechecks every live source member against the captured rows. A changing tree
therefore fails rather than silently producing mixed evidence.

Each materialized copy contains the same declared path/byte rows and the same
generated context. Tests and builders cannot import the caller's source tree:
`PYTHONPATH` names only the current materialized `src`, user site packages are
disabled, and every phase receives a separate writable home.

## Declared build context

`pyproject.toml` now separates the public backend compatibility floor from the
exact environment used for this release lane:

- Python 3.13.5;
- pip 25.1.1;
- setuptools 82.0.1, with public backend floor `setuptools>=77.0.3`;
- pytest 9.0.2;
- `SOURCE_DATE_EPOCH=1784329200`;
- UTC, `PYTHONHASHSEED=0`, disabled pytest plugin autoload, disabled pip index and
  cache, and one-thread defaults for common numerical runtimes.

The lane records Python implementation/cache tag, platform and machine, zlib
compile/runtime versions, build frontend, backend, and exact tool versions. It
fails if the current builder differs from the declaration.

`SOURCE_DATE_EPOCH` is part of the source descriptor rather than ambient process
state. Every materialized file and directory receives that timestamp before
work begins.

## Deterministic permission policy

The source identity intentionally names paths and bytes, not the original mode
bits of a cloudtainer extraction. Release materialization applies one explicit
policy:

- declared files and generated context: 0644;
- materialized directories: 0755;
- revision ZIP members: regular Unix files with 0644 permissions.

`tools/mkrevzip.py` sets those modes after every copy, independent of source
mode and caller umask. `tools/mxrepro.py` verifies them before and after each
phase on POSIX. A phase that changes a declared mode fails as source mutation.

This policy removes accidental mode inheritance from wheel identity. It does not
preserve executable-bit intent; Micromax's declared release set currently has no
executable package member whose execution authority must survive packaging.
Adding one requires an explicit policy change and regression evidence.

## Wheel proof

The lane builds the wheel twice from separate source copies and separate homes
with:

```text
pip --isolated wheel --no-index --no-deps
    --no-build-isolation --no-cache-dir
```

It then verifies each wheel independently:

- safe, unique archive member paths and valid CRCs;
- one matching `.dist-info` directory;
- complete `RECORD` membership, SHA-256 digests, and sizes;
- normalized member timestamps;
- PEP 639 metadata and license placement;
- required package resources, installed docs, plugins, and console entry points.

Success requires byte-identical wheel files *and* identical structured
verification records. The exact first wheel is then installed into a fresh
outside-source target. A `python -I` subprocess imports the installed package,
loads stdlib and screen resources, checks the screen contract, and exercises
installed documentation, plugins, and effect-contract data. This replaces a
wasteful third build with evidence about the artifact intended for publication.

The packaging correction uses the current PEP 639 fields:

```toml
license = "MIT"
license-files = ["LICENSE"]
```

The duplicate manual license data-file is gone. Other installed Micromax docs
and bundled plugins remain declared data files and are probed after installation.

## Receipt and archive binding

After the focused tests, two wheel builds, wheel verification, and installed
artifact probe pass, the lane emits one compact
`micromax.release-receipt.v1` object. The receipt contains:

- the sealed source descriptor and source digest;
- the declared builder/environment;
- focused phase results;
- both wheel names, sizes, hashes, and verification-record digests;
- the assertion that the wheel bytes and verification records agree;
- a self-digest over the receipt payload.

`tools/mkrevzip.py` accepts the receipt only when its tested source identity
matches the archive's recomputed member rows, generated context row,
`SOURCE_DATE_EPOCH`, revision, and epoch origin. It performs bounded strict JSON
reads and rejects duplicate names. Separate archive-A and archive-B copies are
built and must be byte-identical before publication; the selected archive is
verified again from bytes.

The receipt is stored once in the archive manifest rather than duplicated as a
second provenance document. Its self-digest detects accidental or malicious
modification inside the evidence set, but it is not a signature, identity proof,
or transparency-log attestation.

## Small CI lane

`.github/workflows/reproducible-release.yml` invokes the same `make
repro-release` target on `ubuntu-24.04`. It has read-only repository permission,
does not persist checkout credentials, pins Python 3.13.5 and the declared build
tools, and pins `actions/checkout` and `actions/setup-python` to full commit
SHAs. The workflow is deliberately one narrow source/test/wheel/install/archive
job; it does not label focused tests as a complete repository suite.

## Research basis reviewed on 2026-07-17

Primary and project-authoritative sources:

- `SOURCE_DATE_EPOCH` specification and guidance, including deterministic export
  and normalizing source timestamps:
  https://reproducible-builds.org/specs/source-date-epoch/
  and https://reproducible-builds.org/docs/source-date-epoch/
- Python Packaging User Guide on PEP 639 `license`/`license-files` and the
  setuptools 77.0.3 support floor:
  https://packaging.python.org/en/latest/guides/writing-pyproject-toml/
  and https://packaging.python.org/tutorials/packaging-projects/
- Wheel binary distribution and `RECORD` specification:
  https://packaging.python.org/en/latest/specifications/binary-distribution-format/
- GitHub secure-use guidance that a full-length commit SHA is the only immutable
  action reference:
  https://docs.github.com/en/actions/reference/security/secure-use
- Action release/commit identities used by the workflow:
  https://github.com/actions/checkout/releases/tag/v7.0.0
  https://github.com/actions/checkout/commit/9c091bb21b7c1c1d1991bb908d89e4e9dddfe3e0
  https://github.com/actions/setup-python/releases/tag/v6.3.0
  https://github.com/actions/setup-python/commit/ece7cb06caefa5fff74198d8649806c4678c61a1

## Honest boundary

This is reproducibility evidence for one declared Python/toolchain/platform
class, not universal cross-platform reproducibility. Source capture is
file-by-file with before/after and publication rechecks; it is not an atomic
filesystem snapshot against a hostile concurrent writer. Original source mode
bits are normalized by design rather than attested. Non-POSIX mode semantics are
narrower.

The CI job installs exact Python package versions but its downloads are not yet
hash-locked or served from a hermetic dependency snapshot. The receipt is not
signed, the wheel is not published or transparency-logged here, and no SLSA
level is claimed. The test phase is a focused release lane, not the complete
suite. The workflow file is local evidence until a hosting service actually
runs it.
