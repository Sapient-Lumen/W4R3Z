# generated_header_is_derived_not_primary_interface_authority

A crate declares a public `unsafe extern "C"` surface in Rust and uses `cbindgen` to emit a C header.

The important review lesson is that the generated header is a **derived artifact**, not necessarily the primary authority.
The authority receipt must say whether the Rust declarations are primary and whether manual review is still required for signature correctness and foreign-side assumptions.
