# Scenario: Miri + Kani + Verus split truth

A small unsafe-oriented crate has three blocking obligations:

1. a pointer-validity obligation covered by Miri on executed tests,
2. an arithmetic postcondition proved with Kani for a bounded harness,
3. a ring-buffer invariant proved with Verus.

The campaign is **yellow** because one blocking obligation still has only dynamic evidence where policy demands proof-oriented evidence for release approval.
