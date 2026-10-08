# Constant-byte recovery and ZIP snapshot hardening — rev0869

## Material recovery, not registry growth

Two canonical source paths in `INDEX/files.csv` have the same exact identity:
**2 bytes**, SHA-256 `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945`. The literal bytes `[]` match both identities, so
rev0869 restores:

- `sources/ocf_llm/examples/refused_set_empty_v1.json`
- `sources/pact/PACT_workdir/eval_real_registry_semantic_scan/out/violations.json`

The files are accepted only by exact path/size/hash agreement. They parse as
empty JSON arrays; this does **not** prove why they were empty or that the
surrounding refusal/semantic-scan executions were correct.

At-path canonical coverage rises from **101 to 103 files** and exact source
coverage from **14 to 16 files**. Including the 16 historical recovery objects,
**119 files / 4,973,444 bytes** are now rehydratable. **4,467 files /
101,448,546 bytes** remain unavailable.

## Severe local/central ZIP pathname split closed

The rev0868 validator trusted the central-directory pathname while ignoring
non-ZIP64 local extra-field semantics. A generated fixture retained the safe
central name `local-extra/file.txt` but inserted a **local-header-only** Info-ZIP
Unicode Path field (`0x7075`) whose UTF-8 pathname was `../escape.txt`. rev0868
returned `zip_container_valid` for that container.

That is an extractor-disagreement boundary: the PKWARE APPNOTE defines `0x7075`
as a UTF-8 filename representation and expects the same filename storage method
in local and central headers. A validator must not approve one path while an
extractor may consume another.

rev0869 makes the EvidenceVault ZIP profile intentionally strict:

- central extra fields are rejected;
- local extra fields are rejected except for the exact ZIP64 size record emitted
  when fixed local size fields use ZIP64 sentinels;
- local/central flags and extraction versions must match exactly, in addition to
  the existing name, method, CRC, and size checks.

The targeted validator generates the exploit-shaped fixture, proves Python's
central-directory view still contains only the safe names, and requires a
specific `0x7075` rejection. This is a producer-controlled EvidenceVault profile,
not a general-purpose promise to ingest arbitrary ZIP extensions.

## Builder refactor: one source snapshot or no artifact

The prior deterministic builder enumerated paths and reopened them later. A
mutable source tree could change between those phases, so invocation-time input
identity was not frozen even when the resulting ZIP was internally coherent.

The builder now captures every source path plus file SHA-256, size, executable
bit, device, inode, mode, mtime, and ctime before writing. Each file is reopened
without following the final symlink where supported, streamed only if its
identity and digest match the snapshot, and checked again after reading. The
complete source tree is recaptured after writing and after temporary-ZIP
validation. The published path must still name the validated temporary inode and
its SHA-256 must remain unchanged.

Regression tests mutate same-size content, add a late file, and swap a file for
a symlink after capture. Every case must fail without publishing an output.

## Boundaries that remain

Publication remains blocked: no owner-approved root license or notice was added.
All 17 selected StreamFold payloads remain absent. Canonical `README.md` remains
the sole unresolved present-path mismatch. The source snapshot and local
provenance-shaped record are consistency evidence, not a hermetic build or a
signed external attestation.
