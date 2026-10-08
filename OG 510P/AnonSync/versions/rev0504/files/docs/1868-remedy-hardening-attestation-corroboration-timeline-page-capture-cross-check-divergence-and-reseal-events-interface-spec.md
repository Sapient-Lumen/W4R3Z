# Remedy-hardening-attestation-corroboration timeline page — capture, cross-check, divergence, and reseal events

## Purpose

This page records the sequence by which corroboration was achieved, weakened, or rebuilt.
It exists so a later operator can see whether corroboration arose from multiple independent passes or from one narrow capture lane.

## Timeline events

The page must record at least these event classes when present:

- first fresh bundle sealed
- desktop-plane check captured
- WebUI or service-plane check captured
- storage-plane snapshot captured
- runtime-plane check captured
- debug-log capture enabled
- restart-gated evidence collection performed
- contradiction opened
- contradiction resolved
- missing plane satisfied
- independence floor upgraded
- dominant-plane warning raised
- corroboration achieved for named cohort
- corroboration degraded
- corroboration rebuilt and resealed

## Timeline rules

- keep restart-gated capture events visually distinct from always-live evidence
- keep same-world and cross-world corroboration events distinct
- keep contradiction openings and contradiction resolutions separate
- keep stale-plane decay visible even if the seal still stands
- keep reseal visible when corroboration had to be rebuilt after divergence
