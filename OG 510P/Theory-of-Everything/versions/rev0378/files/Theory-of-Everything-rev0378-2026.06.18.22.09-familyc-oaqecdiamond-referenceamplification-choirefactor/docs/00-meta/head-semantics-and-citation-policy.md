# Head semantics and citation policy

## Purpose

The archive previously used "current head" in more than one sense. This surface separates those senses so release packaging, scientific posture, operational use, and public citation do not drift into each other.

## Head fields

| Field | Meaning | Current rule |
|---|---|---|
| `bundle_head` | the revision packaged in the current zip and mirrored in `RELEASE-MANIFEST.json` | advances with each release bundle |
| `scientific_current_head` | the revision whose internal research posture this bundle asserts | normally equals the bundle head unless the bundle is only a metadata repair |
| `release_control_head` | the revision whose custody / authority / rollback machinery controls the bundle's current posture | normally equals the bundle head for custody revisions |
| `operational_head` | the conservative public working head safe for ordinary operational reuse | may intentionally lag behind the bundle head |
| `citation_head` | the conservative externally citable head | may intentionally lag behind the bundle head |

## Non-equivalence rule

A later `bundle_head` does not automatically update `operational_head` or `citation_head`. A cleaner package does not automatically update `scientific_current_head`. A stronger scientific surface does not automatically update public citation safety. Authority transitions and rollback rows are required when the archive treats a posture as changed or reverted.

## Citation rule

External citations should use `citation_head` unless the citing context explicitly needs a later internal custody or research-state revision. Internal continuation should use `bundle_head` plus `scientific_current_head`. Operational reuse should check `operational_head` and the warning line in `SURFACE-STATUS.json`.

## Mirror rule

`START_HERE.md` mirrors these fields through the generated restart block. Hand edits to the mirror are not authoritative; update `SURFACE-STATUS.json` and rerun `make index`.
