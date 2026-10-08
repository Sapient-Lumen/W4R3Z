
# cxx_callback_alias_violation

A mixed Rust/C++ callback path where ownership and aliasing expectations become unclear at the callback boundary.
The point of the fixture is not to prove BorrowSanitizer semantics are final.
It is to show the minimum receiver-facing artifact set needed for review.
