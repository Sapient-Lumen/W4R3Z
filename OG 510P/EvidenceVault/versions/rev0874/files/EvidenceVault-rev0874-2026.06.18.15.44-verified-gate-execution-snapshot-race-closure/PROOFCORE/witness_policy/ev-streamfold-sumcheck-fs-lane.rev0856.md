# rev0856 streamfold sumcheck transcript-binding witness policy

The rev0856 lane is transparent. It has no private witness and no zero-knowledge
claim. All fixture polynomial terms, round polynomials, public context bindings,
derived challenges, and final evaluations are public JSON data.

The verifier may optionally check a separate candidate root for the 17 indexed
canonical streamfold payloads, but that root is only a local admission candidate.
It is not embedded in this overlay and does not alter the rights block.

The lane must reject if challenge derivation omits public context, payload
manifest identity, rights-block state, prior transcript messages, or current round
polynomial coefficients.
