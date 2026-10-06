# Secure Boot integration (host generation binding)

DeriveBSD can optionally bind host generations to a verified UEFI boot chain.

References:
- FreeBSD UEFI Secure Boot overview: https://freebsdfoundation.org/freebsd-uefi-secure-boot/
- FreeBSD SecureBoot wiki: https://wiki.freebsd.org/SecureBoot
- SBAT (generation-based revocation) in shim: https://github.com/rhboot/shim/blob/main/SBAT.md

## Goal
A generation includes/points to:
- the exact EFI boot artifacts
- kernel + module closure
- a boot manifest binding generation → artifact digests

## v1 scope
- “Secure Boot-compatible”: operator signs existing EFI binaries; DeriveBSD records and selects matching artifacts.
- Measured boot/TPM is future, but we define evidence objects early so the lane can be adopted without format churn (see `docs/176-measured-boot-attestation.md`).


## Targeted revocation (bootchain allowlists)

Secure Boot key rotation is a blunt tool. DeriveBSD should additionally support **targeted component revocation** via an SBAT-shaped policy object.

See: `docs/244-bootchain-revocation-and-allowlists.md`, RFC-0176.

Measured boot reference:
- BSDCan 2019: FreeBSD boot process + TPM/measured boot: https://papers.freebsd.org/2019/bsdcan/stanek-improving_security_of_the_freebsd_boot_process/

See RFC-0029.
Last updated: 2026-02-25
