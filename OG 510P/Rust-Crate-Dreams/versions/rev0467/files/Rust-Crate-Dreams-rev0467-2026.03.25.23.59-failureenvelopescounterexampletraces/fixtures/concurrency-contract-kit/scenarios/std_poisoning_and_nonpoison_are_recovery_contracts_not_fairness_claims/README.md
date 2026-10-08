# `std` poisoning and `nonpoison` are recovery contracts, not fairness claims

This scenario exists to keep **P-0538** from flattening panic recovery into fairness or context legality.

`std::sync::Mutex` documents poisoning and the source/docs say poisoning is advisory with an escape hatch.
Nightly `std::sync::nonpoison::Mutex` documents a different, explicit experimental posture.

The fixture protects against saying only “mutex support exists” when recovery posture is materially different.
