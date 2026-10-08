# trim_paths_with_source_lookup_boundary

This scenario exists because path hygiene is increasingly an explicit Cargo / rustc surface, but privacy improvements are not the same thing as a total debugger failure.

The fixture should model a build where path trimming or remapping is enabled and the crate must answer a narrower question:

- did source lookup stay likely,
- did it become weaker or more manual,
- or is the answer honestly `manual_review_required`?

Expected contract behavior:
- `source-lookup-impact.report` records the observed path-hygiene controls.
- `support-posture.report` keeps broad debugger posture separate from source-lookup confidence.
- the crate does not silently absorb full source-diagnosis ownership; deeper diagnosis still belongs with **P-0493**.
