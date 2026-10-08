# cargo-publish-receipt visibility boundaries — 2026-03-20

This note keeps **P-0477 Cargo Publish Receipt Join Kit** from collapsing into fake “release succeeded” language.

A post-publish receipt crate must keep at least these six truths separate:

1. **what local artifact the receipt was based on**,
2. **what Cargo uploaded and whether index polling completed**,
3. **what the registry index now says authoritatively**,
4. **what publish identity is known**,
5. **what public docs/visibility surfaces have converged**, and
6. **what remains partial, delayed, or manual-review-only**.

## What belongs in this lane

The lane is about questions like:

- Did the receipt come from `cargo package`, `cargo publish --dry-run`, a transient publish artifact, an imported CI bundle, or a registry re-download?
- Did the upload complete while Cargo timed out waiting for the index?
- Have checksum and `pubtime` been observed in the index yet?
- Is docs.rs queued, built, failed, or not part of the current receipt?
- Which parts of the receipt are authoritative and which are merely lagging public surfaces?

## What does **not** belong here

Do **not** collapse this seam into:

- trusted-publishing trigger rehearsal (**P-0175**),
- registry-auth/login/download diagnosis (**P-0492**),
- provenance attestations (**P-0015**),
- docs.rs parity / hosted-build explanation (**P-0472**),
- package pre-publish review (**P-0499**),
- or public malware-notification policy.

Those may contribute evidence, but this lane is specifically the receiver-facing contract for **post-publish capture basis**, **authority**, and **visibility state**.

## Preferred artifacts

If this lane keeps sharpening, prefer tiny artifacts such as:

- `capture-basis.receipt.json`
- `receipt-authority.report.json`
- `publication-visibility.report.json`

The point is not to produce another publisher.
The point is to make it reviewable whether a maintainer is looking at:

- `cargo_package_output`,
- `registry_download_reacquired`,
- `index_checksum_and_pubtime_authoritative`,
- `upload_ack_only`,
- `index_visible_docs_pending`,
- or `manual_review_required`.

## LLM/archive reminder

Do **not** let future passes rephrase this seam as:

- “the crate was published,”
- “the checksum matches,”
- “trusted publishing was used,”
- or “docs are available eventually.”

The sharper missing value is a receiver-facing contract that says **what was captured, which observation is authoritative, and which public surfaces have actually converged so far**.
