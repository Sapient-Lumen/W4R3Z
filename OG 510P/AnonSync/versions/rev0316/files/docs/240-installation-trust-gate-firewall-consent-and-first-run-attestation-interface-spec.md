# Installation trust gate, firewall consent, and first-run attestation interface spec

## Purpose

The archive already had upgrade visibility, service promotion, and capability-owner transfer language.
What it still lacked was one stricter contract for the moment before any of that matters:

> when the product is first installed or updated through the operating system, what exactly has been trusted, what user-consent gates remain unresolved, and is the daemon actually ready rather than merely copied onto disk?

Current Resilio docs make this seam concrete.
Their current Windows SmartScreen page still says Defender may block installation because of a new code-signing certificate and may require `Run anyway` or even manual `Unblock` in file properties.
Their silent-install page still says Windows UAC will prompt, firewall changes may still be needed, and the program does not automatically run at the end of installation.

That means package trust, elevation consent, firewall readiness, and first launch are still separate rituals.

## Core decision

AnonSync must treat installation and first-run readiness as one reviewed sequence with explicit attestation.
The product must distinguish:

- package authenticity / signer trust
- elevation consent
- network consent (firewall / port exposure)
- binary copied but daemon not yet started
- daemon started but control surface not yet reachable

The operator must be able to answer:

- what did I just trust
- what prompts were deferred or denied
- is the system merely installed or actually operational
- what remains before the seat can participate safely

## Why this matters

Current Resilio behavior still leaves too much meaning outside the product:

- OS reputation systems can block the installer even when the binary is legitimate
- silent install still may not be fully silent on Windows
- firewall permission can remain unresolved after package copy
- the application may not auto-start at the end of install

AnonSync should therefore hold one stronger rule:

> installation is not complete until trust gates, runtime readiness, and control reachability are all attested.

That still does **not** prove who owns automatic return on later boot/login.
Install receipt and startup-owner truth should stay linked but distinct.

## Fixed review order

Every install, reinstall, or first-run sequence must render the same sections in the same order:

1. **Package trust**
2. **System-consent gates**
3. **Runtime readiness**
4. **Reachability and exposure**
5. **Install receipt**

### 1) Package trust

Show:

- package source
- signer identity or package verification result
- whether the OS raised a trust or reputation warning
- whether the operator bypassed an OS block

### 2) System-consent gates

Show:

- elevation granted or denied
- firewall/network rule state
- service registration state
- shell or protocol registration state if applicable
- any deferred actions still needed for participation

### 3) Runtime readiness

Show one explicit state:

- `installed only`
- `installed and started`
- `started but not yet initialized`
- `started with degraded readiness`
- `ready`

### 4) Reachability and exposure

Show:

- whether the control surface is reachable locally
- whether any network listeners are open yet
- whether share/join actions are safe to perform now
- whether a restart or first-login step is still pending

### 5) Install receipt

Record:

- package verification result
- OS warnings encountered
- prompts granted, denied, or bypassed
- runtime readiness state at completion
- remaining manual tasks, if any

## Main surface

Expose one **Install receipt** and one **Finish setup** page.
The product should use explicit phrases such as:

- `package trusted; runtime not started`
- `runtime started; firewall consent pending`
- `os trust warning bypassed; verify signer and continue`
- `installed but not yet operational`

## Acceptance criteria

This spec is satisfied when:

- package trust and runtime readiness are never conflated
- the operator can tell whether OS warnings were bypassed or cleanly satisfied
- install completion means the seat is truly ready or the remaining blockers are explicit
- first-run networking and control reachability leave an attested receipt
