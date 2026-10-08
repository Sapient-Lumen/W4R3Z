# Cargo package-review lane boundaries — 2026-03-16

This note exists to keep future passes from collapsing multiple publish-adjacent layers into one fake “package security” crate.

## The lane sharpened in this pass

**P-0470 Cargo Package Review Kit** owns the layer above `cargo package` and below publish identity / post-publish confirmation.

Its job is to answer:

> what exact package candidate or workspace package set did we review, what did Cargo normalize or copy into the source bundle, and what source-shape changes need human attention before publish?

That means this lane may legitimately own:

- packaged path inventories,
- workspace candidate-set reports,
- manifest-normalization reports,
- external readme / license copy-in review,
- `.cargo_vcs_info.json` review with explicit non-provenance caveats,
- source-bundle diffs and budget warnings,
- and evidence-source receipts that distinguish direct Cargo facts from conservative explanation.

## Adjacent lanes that must stay separate

### 1. Trusted publishing rehearsal

**P-0175 Trusted Publishing Tooling Kit** answers:

> is this CI workflow/provider/trigger configuration eligible and well-configured for trusted publishing before we attempt a release?

That is about **authorization posture**, not source-bundle shape.

### 2. Post-publish receipt joins

**P-0477 Cargo Publish Receipt Join Kit** answers:

> what happened after publication, what registry/index facts can we confirm, and which release identity did the registry observe?

That is about **after-publish confirmation**, not pre-publish package review.

### 3. Provenance / attestation / malware-response layers

Attestation, provenance, and malicious-package communication crates answer:

> who made this release, can we verify that claim, and what public incident surface exists if things go wrong?

That is not the same as reviewing the packaged source tree.

### 4. SBOM precursor and sidecar lanes

SBOM precursor workbenches and sidecar contract crates answer:

> what machine-readable build/dependency sidecars belong to this artifact and how should they be attached?

That is downstream of packaging review and should not replace it.

## Boundary reminders for future revisions

1. Do **not** let future passes treat `cargo package --list` as if it already solves review. It lists paths; it does not freeze candidate-set, normalization, or explanation truth.
2. Do **not** let future passes treat `.cargo_vcs_info.json` as provenance. The docs explicitly say it is best effort.
3. Do **not** let future passes collapse `-Zpackage-workspace` and trusted publishing into one lane. Workspace package rehearsal and publish authorization are different seams.
4. Do **not** let future passes assume every copied-in file is just another include/exclude rule. External readme/license copy behavior deserves explicit review posture.
5. Do **not** let future passes blur source-bundle review with post-publish registry confirmations.
