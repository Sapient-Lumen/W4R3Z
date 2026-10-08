# Revision 0978 tests

This record separates focused evidence from any complete-suite or cross-platform
claim. Commands ran against the rev0978 working source in this Linux
cloudtainer. Expected Python 3.13 warnings came only from tests that explicitly
exercise legacy `fork` while another thread is live.

## Changed-owner evidence

- The final filesystem/process lifecycle union passed **76/76** in two bounded
  shards: **32/32** argv/shell/open-URL tests in **8.78 s**, and **44/44**
  filesystem/worker-context tests in **10.71 s**.
- The process shard covers same-group and new-session pipe owners, blocked stdin,
  ignored TERM, pidfd identity, start-time fallback revalidation, every exact
  holder, exact-empty-scan non-broadening, no named thread residue, and
  preservation of redirected work.
- The filesystem shard covers real large Queue payloads, receive-before-reap
  ordering, dead-producer early classification, broken-result cleanup, exact
  error tuples, containment swaps, direct mode, and multithread-safe default
  contexts.
- Seven explicit high-risk/consumer checks passed: real large `open_file`,
  `ed.fs-read`, and `ed.fs-list` payloads plus the four batched-stat project,
  recent-file, command-palette, and known-path consumers.

## Adjacent product evidence

- External clipboard import/export, plugin package fingerprint/snapshot budgets,
  and prompt-completion filesystem callers passed **40/40** in **3.43 s**.
- The selected script-filesystem capability journey passed **1/1** with 69
  unrelated cases deselected.

## Structural, generated, and publication-tool evidence

- `python tools/mxeffects.py --check` passed with the generated rev0978 contract
  and 24 effect rows.
- `python tools/mxaudit.py --check` passed with both new lifecycle flags.
- Structural audit plus generated effect-contract tests passed **9/9**.
- Revision-index, context, and living-document hygiene passed **12/12** after
  the publication checkbox, evidence rotation, and generated context were finalized.
- Archive-tool regression coverage passed **52/52**; `mxlint` reported `ok`, and
  its tests passed **2/2**.
- Changed Python modules and tests compiled successfully. Focused Ruff checks
  passed under the repository's existing compatibility ignores; no whole-tree
  Ruff or mypy pass is claimed.

## Archive evidence

The final archive is generated from the cleaned tree with `tools/mkrevzip.py` and
then checked by its embedded-provenance verifier for filename/revision/tag,
source manifest, member digests, CRCs, duplicates, modes, receipt, and lineage.
The resulting filename and verifier result are the publication record for this
revision.

No complete pytest-suite, Windows Job Object, non-Linux escaped-session, hostile
code sandbox, total-memory, syscall, native-crash, corrupt-Queue-frame
preemption, or preemptible process-start claim is made.
