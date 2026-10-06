# RFC-0029: Secure Boot-compatible host activation

- Status: draft
- Created: 2026-02-23

Bind host generations to explicit UEFI boot artifacts and their digests.
Activation emits a boot manifest; `derive explain-boot` reports what booted and why.
