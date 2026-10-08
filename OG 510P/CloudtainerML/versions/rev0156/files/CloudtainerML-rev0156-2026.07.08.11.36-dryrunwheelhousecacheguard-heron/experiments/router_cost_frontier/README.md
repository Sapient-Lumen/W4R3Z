# rev0056 router cost frontier

This experiment stress-tests the row-adaptive sparse-attention router under explicit
QK/value proxy cost weights. It recalibrates the bound-gate router for each
`qk_weight`, evaluates low/middle/high support buckets, and compares against the
simple dense-score mass histogram baseline.

The result is a claim gate: a router win that appears only when QK score work is
assumed much more expensive than value reads is useful systems guidance, but it
is not a measured speed claim.
