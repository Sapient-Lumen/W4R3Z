# Revision 0965 audit

## Priority judgment

The highest-risk unfinished work was the gap between tested source and packaged
source. Archive verification was internally strong, but tests, wheels, and the
archive could each reread a changing working tree. Rev0965 makes one byte capture
the executable release boundary rather than adding another policy document or
registry.

## Corrected findings

1. **Mutable multi-observer release:** tests, wheel builds, installed probe, and
   archives now consume independent materializations of one captured generation.
2. **Broken current packaging:** modern setuptools reproduced a license/data-file
   collision while creating `.dist-info`; PEP 639 metadata and removal of the
   duplicate manual license destination restore wheel construction.
3. **Permission nondeterminism:** identical bytes extracted as 0644 versus 0600
   produced different wheel hashes with no payload differences. Forty-nine
   member external attributes differed. Snapshot files/directories are now
   normalized to 0644/0755 and verified around each phase.
4. **Incomplete source identity:** `SOURCE_DATE_EPOCH`, generated context, revision,
   and epoch origin now participate in the source digest instead of remaining
   ambient release assumptions.
5. **Shared writable state:** each test/build/install/archive phase receives a
   separate home and source copy; ambient Python paths, user site, pip config,
   package index, and pytest plugin autoload are disabled.
6. **Artifact-shape-only comparison:** each wheel now receives independent path,
   CRC, `RECORD`, metadata, timestamp, resource, and entry-point verification;
   both bytes and structured verification records must agree.
7. **Wrong artifact tested:** a redundant third build was removed. The exact first
   wheel chosen for publication is installed outside source and probed with
   isolated Python.
8. **Archive/receipt ambiguity:** the compact receipt is accepted only when its
   source descriptor matches the archive's recomputed members and context. Two
   archive materializations must also be byte-identical.
9. **Duplicated runner policy:** the release lane reuses `mxtoolrun.py` and its
   descendant-process teardown instead of creating another timeout/process tree.
10. **CI tag mutability:** the small workflow uses read-only permission, no
    persisted checkout credentials, and full commit SHA action references.
11. **Umask-sensitive test fixtures:** the first hostile-umask end-to-end run
    showed that two snapshot-verifier unit fixtures inherited 0600/0700 and
    failed before reaching their intended byte/mode mutations. The shared test
    fixture now establishes the declared 0644/0755 baseline explicitly, so the
    release lane itself can be run under `umask 077`.

## Research reviewed on 2026-07-17

The implementation follows the `SOURCE_DATE_EPOCH` specification and
Reproducible Builds guidance, the Python Packaging User Guide's PEP 639 metadata
and setuptools support floor, the wheel/`RECORD` specification, and GitHub's
secure-use guidance for immutable action references. Exact source links and the
Micromax implications are in
`docs/921-single-source-reproducible-wheel-release-receipt.md`.

## Waste removed

No generic attestation framework, release database, builder registry, third
wheel build, second receipt format, or release-specific process supervisor was
added. The lane is one executable coordinator over existing context, audit,
effect, package, archive, and subprocess owners. Failed attempts and build trees
remain outside the revision archive.

## Residual risk

- File-by-file capture plus rechecks is not an atomic snapshot against a hostile
  concurrent writer.
- Reproduction is established only for the declared toolchain/platform class;
  Windows, other Python versions, other zlib builds, and other architectures are
  not claimed.
- Mode normalization deliberately discards original permission intent; adding an
  executable release member requires a new policy.
- CI builder packages are exact-version but not hash-locked or hermetically
  mirrored, and the workflow has not become evidence until a hosting service runs it.
- A receipt self-digest is not a signature, authorship proof, transparency log,
  or supply-chain attestation.
- The focused lane is not a complete repository suite.
