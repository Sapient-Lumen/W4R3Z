# rev0871 — embedded digest recovery and safe materialization refactor

## Result

This revision restores **two exact canonical source payloads / 144 bytes** and replaces three independent recovery-publication implementations with one descriptor-bound, no-clobber boundary.

The recovered paths are:

- `sources/ocf_llm/examples/pcb_equivocation_demo_v238/subject_1.digest.txt`
- `sources/ocf_llm/examples/pcb_equivocation_demo_v238/subject_2.digest.txt`

For each file, the cumulative patch preserves the complete `sha256:<digest>` value inside `equivocation_report.json`. Appending one LF yields 72 bytes, and those bytes independently match the path-specific full SHA-256 in `INDEX/files.csv`. No partial hash or semantic plausibility was accepted.

## Coverage movement

Exact current-path coverage rises from **107 to 109 of 4,586 files** and exact source coverage from **20 to 22 of 3,476 files**. With the 16 protected historical recovery objects, **125 files / 4,973,641 bytes** are now rehydratable. **4,461 files / 101,448,349 bytes** remain unavailable.

## Refactor: one write boundary instead of three

`scripts/safe_materialize.py` now owns exact-byte publication for the patch-corpus, overlay-history, rev0870 low-entropy, and rev0871 embedded-evidence recovery tools. The old implementations mixed pathname checks, temporary files, hard links, and cleanup rules. Even where each implementation appeared reasonable, divergence made future fixes easy to miss and had already produced one destructive-cleanup defect in rev0870 development.

The shared boundary:

- rejects path aliases, traversal, root symlinks, parent symlinks, and non-directory parents;
- walks or creates parents through verified directory descriptors;
- creates the final file with `O_EXCL` and never replaces a pathname;
- normalizes mode to `0644`, fsyncs, and verifies size and SHA-256 by reading the opened descriptor;
- verifies that the pathname still names the created inode;
- removes a failed output only when this invocation created that same inode; and
- accepts a race winner only when its exact bytes are independently verified.

The targeted suite demonstrates preservation of mismatched pre-existing bytes, preservation of an `O_EXCL` race winner, rejection of parent/final/root symlinks, and rejection of traversal aliases.

## Recovery frontier: what was closed instead of ritualized

### Root README

The indexed canonical `README.md` is 10,499 bytes with SHA-256 `0255c297…`. Reversing the retained overlay chain reaches a 623-byte rev0840 overlay README, not the canonical identity. The history does not contain the missing byte stream. The mismatch remains honestly unresolved.

### Old-side patch streams

The patch corpus was also examined bidirectionally rather than only for complete new-side streams. Complete old-side streams produced no newly missing indexed payload. That avenue is now a measured negative result, not a recurring hunch.

### Embedded evidence

A broad bounded scan of surviving lines, tokens, scalar values, JSON subobjects, and line-terminated variants tested roughly 530,830 candidate identities. Only the two PCB subject digest paths matched complete path-specific index identities.

### PACT content-addressed store

There are 174 absent PACT store objects totaling 6,356 bytes. Every filename embeds the same SHA-256 recorded by the index, and their sizes form a conspicuous 10/90/20/54 distribution across 34/35/38/39 bytes. That makes them a high-value recovery family, but not a license to guess. Bounded compact-JSON schema trials and exact-name public search yielded no verified preimage, so **zero PACT objects were admitted**.

## Remaining priority

The largest unfinished risks are still external-decision or external-byte problems: owner-approved root/component rights, all 17 selected StreamFold payloads, and the canonical root README. Further local work should be admitted only when it recovers exact bytes, removes a demonstrated correctness defect, or directly closes those blockers.
