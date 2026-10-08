# Archive claim-upgrade discipline — 2026-03-25

This note is archive hygiene for humans and LLMs.

The repo now has enough breadth that it is easy to accidentally upgrade a claim too quickly.
So the archive should use an explicit **claim ladder**.

## Claim ladder

### Level 0 — observed surface
Examples:
- crates.io shows a `Security` tab
- docs.rs exposes rustdoc JSON
- a goal page exists for Cargo SBOM precursor
- a project page lists many GUI or web crates

These are useful facts.
They are **not yet** receiver-facing support guarantees.

### Level 1 — interpreted posture
Examples:
- a crate likely has more visible trust posture now
- docs/build/target truth is becoming more machine-usable
- a domain appears active enough that seam kits may beat umbrella rewrites

These are archive inferences.
They must be labeled as such.

### Level 2 — imported support contract
Examples:
- this crate imports docs.rs build metadata plus target metadata into one report
- this crate imports public-boundary signals into a semver-facing witness bundle

This is stronger because a crate has turned raw substrate into a bounded artifact.

### Level 3 — composite crate contract
Examples:
- this crate can honestly help a team choose, freeze, recheck, and transition
- this crate can explain support ceilings under mirror/offline constraints

Only promote to this level if the repo can point to real artifact families and refusal boundaries.

### Level 4 — desired ecosystem state
Examples:
- this should become part of Cargo
- this should be a default team workflow

This is aspiration, not present truth.
Keep it separate.

## Rules for upgrading claims

1. Do not move from **observed surface** to **support promise** in one step.
2. Do not treat community ecosystem hubs as if they were official compatibility authorities.
3. Do not treat a goal page as if the work were already stabilized or shipped.
4. Do not treat one solved scenario as universal coverage.
5. Do not erase older basis when the new pass only adds one more signal.
6. When promoting a lane, name the new artifact family that justified the promotion.

## Required note when reasoning changes materially

A pass that materially changes ranking or scope should leave behind:
- a source-basis note,
- one paragraph of fact / inference / open-question separation,
- and a note about what claim level actually changed.

## Anti-amnesia / anti-ghost-synthesis rules

Future archive passes should not:
- repeat a previous conclusion without checking whether its source basis still exists,
- paraphrase old inference as if it were fresh fact,
- or widen a lane by vibe instead of by artifact seam.

When reopening a lane, first ask:
- what was previously known,
- what source basis supported it,
- what new source has arrived,
- and whether that new source justifies a true claim upgrade.

## Takeaway

The archive should become stricter over time about how it strengthens claims.
That makes later synthesis more trustworthy and reduces LLM-induced drift.
