# FT-0074 closure

Closed in rev0075.

Decision: TimeSync needs a compact transparency trust-policy reference, but only as detached replay-transparency policy-binding metadata. The reference is digest-bound and summary-only. It does not import a trust-policy language, witness registry, monitor registry, trust-anchor set, proof format, gossip transcript, or external provenance graph.

rev0075 adds `transparency_trust_policy_reference`, extends profile compatibility statements with the `replay_transparency_policy_equivalence` workflow, and adds semantic tests for policy-reference misuse and weaker threshold equivalence.
