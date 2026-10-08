# Flux and Verus partial scope require explicit obligation inventory

This scenario keeps **strong partial coverage** separate from **whole-campaign closure**.

Flux can give compile-time refinement evidence for one slice of the crate while Verus can prove a stronger theorem-oriented slice elsewhere.
A campaign should not go green unless the obligation inventory makes it clear which obligations exist and which ones are still uncovered.
