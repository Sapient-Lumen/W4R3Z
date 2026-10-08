# 706 — Release maintainer handoff and source-review triage

**Track:** Shared / Release maintenance

**Status:** Release-hardening note for v831

v831 adds a bounded maintainer handoff layer. The archive already has a synthetic pilot harness, expected-success verifier outputs, negative-control expected-failure fixtures, evaluator scoring, trust-recovery handoff, and human-review handoff. What was still missing was a compact release-maintenance surface that answers four questions before a new ZIP is published:

1. Which synthetic outputs are current for this version?
2. Which release-gate inventory is the maintainer relying on?
3. Which external-source reviews are expired or due soon?
4. Which parts are still explicitly synthetic, pre-pilot, and non-certifying?

## Added artifacts

- `artifacts/registries/release-maintainer-handoff.csv`
- `tools/release_maintainer_handoff_pack.py`
- `scripts/check_release_maintainer_handoff.py`
- `artifacts/reports/release-maintainer-handoff.json`
- `artifacts/reports/release-maintainer-handoff.md`
- `artifacts/reports/source-review-triage.json`
- `artifacts/reports/source-review-triage.csv`

The generated handoff report summarizes current Example County synthetic outputs, gate-step inventory, source-review pressure, handoff actions, key artifact digests, and residual non-live items.

## Source-review triage rule

The source-review triage report is not a claim that any external source is wrong. It is a maintainer queue. It groups sources into pinned, expired-review, due-within-30-days, due-later, missing-review, high-risk-special-case due soon, and official-website due soon buckets.

For v831, expired source-review windows are release-blocking in the handoff check. Due-soon rows are not release-blocking, but they are explicitly visible so a maintainer cannot treat unpinned references as durable authority without review.

## Handoff is not the release gate

`tools/release_maintainer_handoff_pack.py` does not replace `scripts/release_gate.py`. It gives a reviewer a small, current summary that should make the release gate easier to audit:

```bash
python3 tools/release_maintainer_handoff_pack.py --json
python3 scripts/check_release_maintainer_handoff.py
python3 scripts/release_gate.py
```

The generated handoff says what the release believes about itself. The release gate still decides whether the tree is internally consistent.

## Non-claim boundary

The handoff report is not live election evidence, not certification, not outcome proof, not proof of intent or fraud, and not legal advice. It is also not a transcript proving that a particular maintainer ran every gate in a particular shell. It is a deterministic summary of the archive state and should be sealed by `MANIFEST.sha256` like any other release artifact.

## Failure meaning

If `scripts/check_release_maintainer_handoff.py` fails, the release may have one of these problems:

- the handoff JSON or Markdown is stale;
- the source-review triage report is stale;
- a current synthetic output is no longer a PASS;
- source-review windows have expired at release date;
- the handoff registry references files that do not exist;
- the public handoff summary no longer carries synthetic/non-certification boundary language.

Treat this as release-maintenance drift. Fix the underlying artifact or regenerate the handoff pack before sealing the ZIP.
