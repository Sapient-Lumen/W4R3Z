# Research notes: deterministic convergence semantics

Rev0856 does not claim that AnonSync is a CRDT. It adopts a narrower proof target from the replicated-data literature: replicas that have incorporated the same updates need deterministic conflict semantics and the same materialized result.

Primary references reviewed:

- Shapiro, Preguiça, Baquero, and Zawirski, *A comprehensive study of Convergent and Commutative Replicated Data Types* (2011): https://inria.hal.science/inria-00555588/document
- Shapiro et al., *Conflict-free Replicated Data Types* (2011): https://inria.hal.science/inria-00609399v1/document
- Almeida, *Approaches to Conflict-free Replicated Data Types* (2023): https://arxiv.org/abs/2310.18220
- Zhang, Wei, and Huang, *Remove-Win: a Design Framework for Conflict-free Replicated Data Types* (2019): https://arxiv.org/abs/1905.01403
- Kleppmann and Beresford, *A Conflict-Free Replicated JSON Datatype* (2016): https://arxiv.org/abs/1608.03960

Implications for AnonSync:

- Conflict resolution must be independent of which replica labels a value “local.”
- Concurrent add/remove semantics are a product policy, not an implementation accident; rev0856 deliberately chooses tombstone-wins for the narrow file/delete case.
- Total-order arbitration can produce a deterministic primary, but retaining losing user bytes is a separate product obligation.
- Delivery-order permutation and duplicate-delivery tests are necessary but insufficient. Causal context, object recreation, rename, compaction, and dissemination must be modeled before claiming strong eventual consistency.
- Tombstones eventually need causal-stability and retention policy; keeping them forever is operationally wasteful, while collecting them too early risks resurrection.

Speculative direction: treat the control plane as an authenticated causal operation set with explicit object and key epochs, and treat encrypted content chunks as an opaque data plane. A small reference model should define merge semantics; C++ should be tested against generated histories rather than relying primarily on source-shape audits.
