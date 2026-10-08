# FFI callback round trip keeps boundary partial despite green run

This scenario models a local harness where Rust calls into foreign code and receives a callback into Rust.

Even if the harness looks green, callback behavior, symbol loading, and foreign-side aliasing rules stay only partially visible to the local witness.
