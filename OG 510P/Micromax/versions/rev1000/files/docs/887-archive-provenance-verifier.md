# Archive provenance verifier (rev0929)

Rev0929 consumes the archive-member provenance that rev0926 began embedding in
`MICROMAX-CONTEXT.json`.  The risky gap was not that revision zips lacked hashes;
it was that nothing in the cube could prove that a linked zip still matched its
embedded manifest after packaging, upload, copy, or tampering.  This revision
turns that from a prose promise into an executable verifier.

## Online research used

- Python's current `zipfile` documentation says `ZipFile.testzip()` reads all
  files in an archive and checks CRCs/file headers, returning the first bad
  member or `None`.
- The same `zipfile` documentation warns that ZIP path handling APIs do not
  sanitize member names for callers; callers inspecting untrusted archive paths
  remain responsible for rejecting absolute paths and `..` traversal.
- SLSA's provenance model is centered on a claim that a builder produced an
  artifact from declared inputs/materials; its requirements and distribution
  guidance keep artifact integrity and provenance tied to the produced artifact.
- OWASP SCVS frames supply-chain vigilance as a set of verification activities,
  controls, and best practices rather than a static bill of materials alone.

Sources re-read:

- https://docs.python.org/3/library/zipfile.html
- https://slsa.dev/spec/v1.0/requirements
- https://slsa.dev/spec/v1.0/distributing-provenance
- https://slsa.dev/spec/draft/build-provenance
- https://owasp.org/www-project-software-component-verification-standard/

## What changed

- `tools/mkrevzip.py` now exposes `verify_archive(path)` plus
  `python tools/mkrevzip.py --verify-archive <zip>`.
- Normal `mkrevzip` packaging self-verifies the archive it just wrote before it
  prints the path.
- Verification rejects duplicate member names, unsafe member names, unexpected
  directory entries, absent or malformed manifests, wrong manifest archive names,
  missing provenance, schema mismatches, member-set differences, per-file
  byte/hash differences, and aggregate digest/count/byte mismatches.
- Verification has explicit member, compressed-byte, and uncompressed-byte
  budgets before reading archive payloads, so the verifier itself does not become
  an unbounded zip-bomb reader.
- `make revzip-verify ZIP=...` gives the handoff lane a small inspection command.
- `tools/mxaudit.py --check` now hard-checks the verifier seam as
  `mkrevzip_verifier_present` / `mkrevzip verifier present=True`.

## Why this was high leverage

The linked zip is the datacube.  If the session handoff artifact can carry a
manifest but no tool consumes it, the manifest becomes comforting but weak.  The
new verifier does not claim SLSA-grade signed provenance or reproducible builds;
it does close the local integrity loop for the exact archive a future session
receives.

This is also a useful audit/refactor because the release-hygiene proof moved
from scattered expectations into one owner function:

- provenance production remains `archive_member_rows()` /
  `archive_member_provenance()`;
- provenance consumption is now `verify_archive()`;
- the CLI and Makefile target call that owner instead of each test or future
  script re-parsing the manifest by hand.

## Validation run in this cloudtainer

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src pytest -q tests/test_mkrevzip.py
# 13 passed, 1 expected duplicate-member warning

PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src pytest -q tests/test_mxaudit.py tests/test_mxcontext.py
# 7 passed

PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src pytest -q tests/test_mxcontext.py
# 5 passed

python tools/mxlint.py
# mxlint: ok

PYTHONPATH=src python tools/mxaudit.py --check
# ok; human output includes mkrevzip verifier present=True

PYTHONPATH=src python tools/mxcontext.py --check
# ok after the rev0929 context refresh
```

A combined `pytest -q tests/test_mkrevzip.py tests/test_mxaudit.py` selector was
attempted, but the outer tool timeout cut it off after the mkrevzip file had
completed.  The same files were therefore validated as split selectors above,
which is the honest cloudtainer evidence for this revision.

## Remaining risks and next work

1. **This is not signed provenance.** Add an optional detached digest/signature
   or SLSA-style attestation only after the local verifier remains stable.
2. **Dependency inputs are still not locked.** Release hygiene still needs a
   dependency lock or explicit no-lock policy with package inspection.
3. **Archive revision and package version policy remains loose.** The zip
   revision and `pyproject.toml` package version should eventually have a clear
   relationship.
4. **Verifier budgets are coarse.** The defaults are intentionally generous for
   Micromax zips; future packaging lanes can tune them from observed archive
   size history.
5. **Do not turn this into ceremony.** The next runtime step should still be a
   concrete owner/lifetime seam, not a hand-maintained registry of every effect.
