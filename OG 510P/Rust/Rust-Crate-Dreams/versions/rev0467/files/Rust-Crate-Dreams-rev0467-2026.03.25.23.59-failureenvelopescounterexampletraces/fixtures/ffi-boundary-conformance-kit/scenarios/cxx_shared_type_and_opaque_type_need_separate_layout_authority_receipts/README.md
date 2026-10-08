# cxx shared type and opaque type need separate layout-authority receipts

This scenario exists to stop one `cxx` bridge from quietly claiming a single representation story.

`cxx` explicitly distinguishes:

- **shared types** that both languages can see and may pass by value, and
- **opaque types** that must cross behind an indirection such as references or smart pointers.

A worthy contract crate should therefore emit different layout-authority receipts for those surfaces.
