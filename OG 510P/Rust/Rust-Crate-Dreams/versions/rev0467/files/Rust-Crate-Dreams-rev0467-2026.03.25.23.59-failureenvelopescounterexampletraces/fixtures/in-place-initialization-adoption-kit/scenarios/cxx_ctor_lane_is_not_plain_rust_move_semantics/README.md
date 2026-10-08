# Scenario: C++ constructor lane is not plain Rust move semantics

An interop layer uses `moveit`/Crubit-style constructors. The review object must not flatten those into ordinary Rust by-value construction or memcpy-style moves.
