# Mission audit — REV0114

Status: `pass_with_blockers`  
Promotion allowed: `false`

## What changed

rev0114 focuses on the cold-reviewer failure mode: a portable public-trace handoff archive could be correct by digest but still too easy to verify incorrectly after extraction. The handoff gate now auto-discovers `PUBLIC_TRACE_HANDOFF_MANIFEST.json` at the archive root, `VERIFY_HANDOFF.py` delegates to the bundled strict gate, and the direct gate remains canonical because it validates the launcher itself by digest.

## Risk reduced

- No-argument direct verification works from a moved/extracted archive.
- The convenience launcher is included in the toolpack subject set rather than silently trusted.
- A tampered launcher is rejected by the direct gate.
- Running the launcher from the full cube root cannot produce a false green when no handoff manifest is present.

## Still blocked

This revision is not promotion evidence. The project still needs a real public TinyLlama trace NPZ/provenance pair, an accepted evaluation receipt, selector-entry handoff, a portable real handoff archive, selector/cost evaluation, and named-hardware timing.
