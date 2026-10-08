# rev0077 post-transform contract note

The riskiest unfinished path after rev0076 was not another provenance rule; it was the missing executable bridge between raw model projections and the actual tensors scored by attention.

rev0077 adds that bridge as a synthetic contract harness, not as public-model evidence. The harness generates raw Q/K/V projection states, applies a RoPE-like transform to Q/K, records explicit attention scale and finite causal/padding score bias, writes `qkv_npz_v2`, and asks the existing gate to replay it. The post-transform bundle reconstructs its dense reference exactly. The raw-projection negative-control bundle carries the same reference but uses pre-transform Q/K, and therefore fails the dense-reference contract.

This makes the semantic failure concrete and reusable:

- raw projection tensors can have valid shape, provenance-looking metadata, and deterministic replay while still being the wrong scientific object;
- post-transform Q/K/V must be paired with the exact score rule, including scale and mask/bias;
- synthetic self-attestation cannot be promoted to public/pretrained evidence, even with a detached manifest;
- the remaining blocker is no longer whether the cube has a contract, but whether a real public model can be captured under it.

Current blocker: implement or run a real architecture-aware Hugging Face adapter, or move to named-hardware sparse-kernel evidence, or stop/pivot the lane.
