# library_defines_getrandom_backend_instead_of_root_crate

This scenario exists to keep **P-0519** honest about **authority ownership**.

`getrandom` makes the custom-backend boundary unusually explicit: the backend should ideally live in the root crate, must be defined only once, and upstream libraries should not define it outside tests/benchmarks.

A worthy authority-surface crate should capture that the entropy-origin choice is **owned by the application/root crate**, not silently by a library dependency.
