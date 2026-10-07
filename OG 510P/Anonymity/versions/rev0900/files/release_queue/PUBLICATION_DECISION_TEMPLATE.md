# Publication decision template

This template is **non-authorizing until copied into `release_queue/decisions/` as a dated decision note and completed without placeholders**. It exists so the publication helper and future reviewers agree on the minimum manual gate surface.

Required publication block:

```text
Decision: <human-readable decision title>
Publication action: publish
Publication date: YYYY.MM.DD
Source: series/.../paper.tex
Source SHA-256: <64 lowercase hex>
Published name: YYYY-MM-DD_slug_title
Published path: published/YYYY-MM-DD_slug_title
Evidence pack manifest: release_queue/evidence_packs/<id>/EVIDENCE_PACK_MANIFEST.json
Compile witness: release_queue/FREEZE_COMPILE_WITNESS.json
Freeze packet manifest: release_queue/freeze_packets/<id>/FREEZE_PACKET_MANIFEST.json
Unicode/control hygiene: reports/unicode_control_hygiene.json must pass for the current revision
Queue note: release_queue/published_ready/<id>.md
Public citation-head update: required
Publication receipt: required after guarded helper execution
Publication authorized by this completed note: true
```

Required rationale block:

```text
Rationale:
- Why this source is being published now:
- Why the evidence-pack obligation is satisfied or explicitly waived:
- Why the compile witness is current for this revision:
- Why Unicode/control-character hygiene is clean for this revision:
- What public citation head will be added:
- What post-publication surfaces must be regenerated:
```

Minimum command shape, after the note is completed and saved:

```bash
python3 -B publishing/create_published_entry.py \
  --root . \
  --date YYYY.MM.DD \
  --title "<Title without Anonymity prefix>" \
  --source series/.../paper.tex \
  --expected-source-sha256 <64 lowercase hex> \
  --decision-note release_queue/decisions/<dated-publish-decision>.md \
  --evidence-pack release_queue/evidence_packs/<id>/EVIDENCE_PACK_MANIFEST.json \
  --compile-witness release_queue/FREEZE_COMPILE_WITNESS.json \
  --freeze-packet release_queue/freeze_packets/<id>/FREEZE_PACKET_MANIFEST.json
```

After the helper succeeds, regenerate publication classification, citation heads, public surface, provenance, schemas, manifests, and archive reports before packaging. The template itself does not publish anything.
