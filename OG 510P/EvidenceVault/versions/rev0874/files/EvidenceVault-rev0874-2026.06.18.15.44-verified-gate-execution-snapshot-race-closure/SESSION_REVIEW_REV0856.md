# Session review — rev0856

The riskiest active gap was the rev0855 toy sumcheck transcript accepting explicit
challenge values. rev0856 closes that harness gap by deriving challenges from a
public transcript-binding contract and adding reject fixtures for bad challenge
and omitted public-context binding.

The 17 canonical streamfold payloads remain absent. The new payload admission
contract describes how a future candidate root must satisfy exact path, byte, and
SHA-256 checks before any recovered payload lane should be considered.

The proofcore verifier surface was also audited/refactored so rev0855 is a
historical parent checkpoint and rev0856 is the active lane.
