# Cargo artifact handoff lane boundaries — 2026-03-16

This note keeps the archive from flattening several nearby Cargo artifact ideas into one fake “artifact output crate”.

## Main judgment

Cargo now has enough output substrate that **final-artifact handoff** deserves its own sharper lane.
But that lane still sits beside several neighbors that should remain separate:

1. **produced-artifact handoff bundles**
2. **artifact↔sidecar association and shipping policy**
3. **build-dir consumer migration and layout dependence**
4. **build-script / artifact-dependency upstream substrate**
5. **historical build-analysis storage and replay**
6. **publish identity / release receipts**

Those layers compose.
They should not be collapsed.

## The layers

### 1. P-0471 Cargo Artifact Handoff Kit

This is the lane for:

- what final artifacts a build produced,
- which package / target / profile owns each promoted output,
- how those facts were captured,
- and what a downstream CI job, packager, or external build system should import.

It answers:

- what outputs exist,
- why the bundle believes those outputs are the right promoted artifacts,
- and whether the artifact mapping is exact, copied-output exact, conservative, or manual-review-only.

It does **not** need to own sidecar schema drift, build-dir migration policy, or registry publish truth.

### 2. P-0479 Cargo Artifact Sidecar Contract Kit

This is the lane for:

- which companion files belong to which artifact,
- whether those files should ship,
- and how sidecar schema/version drift should be reported.

It is narrower than P-0471.
P-0471 can say “artifact X exists and is the promoted output”; P-0479 says “sidecar Y belongs to artifact X and ships (or does not ship) for reason Z”.

### 3. P-0489 Cargo Build-Dir Consumer Transition Kit

This is the lane for:

- tools that still touch build-dir / target-dir internals,
- transition receipts for `-Zbuild-dir-new-layout`,
- and migration plans away from internal directory assumptions.

P-0489 asks whether a consumer should keep scraping layout details at all.
P-0471 is one possible destination when the honest answer is “no, this consumer just wants final artifacts”.

### 4. P-0508 / P-0495 upstream artifact-production lanes

This includes:

- delegated build-script units,
- build-script metadata handoff,
- and artifact dependencies / custom final artifacts.

These crates are about **how artifacts come into existence upstream**.
P-0471 is about the **downstream handoff bundle after the build has happened**.

### 5. Build-analysis history

Cargo build-analysis work is about:

- session IDs,
- rebuild reasons,
- timings,
- and persisted historical build information.

P-0471 may link to a session ID when available.
That does **not** make it a general historical build-analysis crate.

### 6. Publish-surface identity crates

Trusted publishing and post-publish receipt joins answer:

- who published,
- under which CI identity,
- and how local package facts joined to registry facts.

An artifact-handoff bundle may exist without any publish action at all.
That is a clue that these are separate lanes.

## Anti-patterns to avoid

### Anti-pattern 1: “artifact-dir solves handoff”

`--artifact-dir` is useful copied-output help.
It is not, by itself:

- an ownership manifest,
- an origin receipt,
- or a diffable handoff bundle.

### Anti-pattern 2: build-dir migration and final-artifact handoff are the same thing

Testing `-Zbuild-dir-new-layout` may reveal that a consumer should stop depending on layout internals entirely.
That does not mean the build-dir migration crate and the artifact-handoff crate are the same product.

### Anti-pattern 3: historical sessions equal handoff truth

A session ID can help link a bundle to one Cargo invocation.
It does not replace the handoff manifest that downstream consumers actually need.

### Anti-pattern 4: build-script-created outputs are automatically exact

Build-script-produced final artifacts still need explicit origin labeling.
When the upstream custom-final-artifact story is incomplete, `manual_review_required` is an honest success state.

## What future passes should do

When touching P-0471 or nearby lanes, state explicitly:

1. whether the crate owns **produced-artifact handoff**, **sidecar association**, **build-dir transition**, **artifact production substrate**, **historical session storage**, or **publish identity**,
2. which facts came from stable Cargo messages,
3. which facts depended on `--artifact-dir`, build-script metadata, or imported build-analysis sessions,
4. which file in the bundle carries origin and exactness truth,
5. and where manual review still remains necessary.

That honesty is part of the product.
