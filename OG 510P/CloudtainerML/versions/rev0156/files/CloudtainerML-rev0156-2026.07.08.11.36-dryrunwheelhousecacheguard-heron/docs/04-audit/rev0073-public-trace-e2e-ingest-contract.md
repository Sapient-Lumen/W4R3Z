# rev0073 — public trace E2E ingest contract

This revision hardens the highest-priority blocker: actual public/pretrained attention traces.

The local capsule cannot capture such a trace because it has PyTorch CPU but lacks `transformers`, TransformerLens, and a sampled local Hugging Face model cache. Instead of creating another surrogate claim, rev0073 makes the capture path fail-closed:

- the HF capture helper now writes NPZ self-attestation metadata;
- it can also write a JSON provenance manifest;
- the public trace gate accepts public/pretrained status only when the manifest and NPZ self-attestation agree;
- forged public manifests for local fixtures are rejected.

This is not public/pretrained evidence. It is the executable contract needed before the next environment-specific capture run.
