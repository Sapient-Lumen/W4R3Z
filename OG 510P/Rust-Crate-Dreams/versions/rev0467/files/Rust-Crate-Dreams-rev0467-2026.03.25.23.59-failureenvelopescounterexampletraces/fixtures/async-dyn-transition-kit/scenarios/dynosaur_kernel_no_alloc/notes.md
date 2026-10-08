
# dynosaur_kernel_no_alloc

A constrained environment wants dynamic dispatch over async-like traits but is suspicious of ordinary heap-allocation assumptions.
The key planning question is whether the chosen recipe is really comparable to the existing public promise, or whether it changes allocation and operational expectations too much.
