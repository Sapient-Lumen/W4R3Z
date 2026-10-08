# Claude feedback (rev142) — temporary vendored sources

**Purpose:** keep the Claude rev142 feedback bundle available *during active integration* so archive edits can cite the exact normative requirement being merged without copying large text.

**Person served:** maintainers who need to integrate external review systematically while keeping the archive small.

**From-below:** This prevents “feedback becoming doctrine” by making removal explicit—once the feedback is integrated, this folder must disappear.


## Not part of the archive
These files are **inputs to a revision process**, not archive artifacts.
They are vendored only so existing citations like `../sources/claude-feedback/rev142/...` resolve inside the distributed zip while integration is ongoing.

This implements Claude rev142 **Part 3 §14b** (“Deprecation of this feedback”): feedback should be integrated (or explicitly rejected with reasons), then discarded.


## Removal target
Delete this folder when **both** conditions are true:
1. No files under `archive/` reference `sources/claude-feedback/rev142/` (i.e., all feedback citations have been replaced by internal canonical anchors).
2. `archive/100-claude-feedback-integration-tracker.md` records the remaining Claude rev142 items as DONE (or explicitly rejected with reasons).

Suggested check (run from repo root):
```bash
grep -R "sources/claude-feedback/rev142" -n archive/ || echo "OK: no remaining Claude-feedback citations"
```


## How to retire citations without bloat

**New default:** cite `archive/101-claude-rev142-normative-requirements.md` (or the canonical internal anchors it lists) instead of citing these raw feedback files directly. This keeps traceability while shrinking the dependency on this folder.
As integration completes, replace citations to these files with citations to **canonical internal locations** that now embody the requirement (typically `96`, `98`, `70`, `31`, `08`, `36`, `03`, or the relevant domain memo).
Avoid copying prose from the feedback; prefer a one-line internal pointer.


**Working note (rev284):** a detailed integration working doc was moved out of the archive and preserved here as `integration-tracker-detailed.md`; the archive uses the compact `archive/100-claude-feedback-integration-tracker.md` going forward.
