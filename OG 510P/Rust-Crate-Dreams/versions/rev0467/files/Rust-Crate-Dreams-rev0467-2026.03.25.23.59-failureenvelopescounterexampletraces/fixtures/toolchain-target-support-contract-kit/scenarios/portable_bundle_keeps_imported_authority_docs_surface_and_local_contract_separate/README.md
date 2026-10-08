# Scenario — portable bundle keeps imported authority, public docs surface, and local contract separate

This scenario exists to keep **upstream support authority**, **public docs surface**, and **project-local support promises** separate.

The project exports one portable review bundle for an embedded gateway crate.
The bundle includes imported Rust-project tier facts, docs.rs public-surface receipts, local support-surface and readiness reports, and host/target topology receipts.
A serious support-contract crate should keep those artifacts separate so a reviewer can see that hosted docs and rustup availability are helpful context, not automatic proof of release-grade support.
