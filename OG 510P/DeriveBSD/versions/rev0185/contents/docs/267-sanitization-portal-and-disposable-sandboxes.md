# Sanitization portal and disposable sandboxes (Dangerzone lessons)

Opening “untrusted documents” is a perennial sharp edge: PDFs and office formats routinely act as exploit containers.
Many high-assurance workflows solve this by *rendering* the document inside a hardened sandbox and exporting only pixels (optionally OCR’d).

DeriveBSD is greenfield enough to bake this in as a **first-class capability**, not a pile of ad-hoc scripts.

Related: treat inbound bytes as labeled imports with quarantine metadata (`docs/280-origin-labels-and-quarantine-attributes.md`). The sanitize portal is one of the default import operations.

## Goal

Provide a standard, policy-governed way to:
- ingest an untrusted document
- convert it inside a **disposable, no-network sandbox**
- emit a **sanitized artifact** (and receipts) suitable for export to less-trusted domains

## Design sketch

### 1) A dedicated portal: `sanitize`
Expose a portal method (name illustrative):
- `org.derivebsd.portal.Sanitize.SanitizeFile(input_handle, profile, opts) -> sanitize.receipt`

The portal:
- never grants ambient filesystem access
- accepts only explicit input handles (from FileChooser / Documents portal)
- returns only explicit output handles
- emits a consent receipt when interactive approval is required

### 2) Sanitization runs as a disposable workload
Sanitization executes in a disposable compartment (microVM preferred; jail fallback possible):
- *no network* (hard default)
- minimal device surface
- tight CPU/mem/time budgets
- deterministic input/output staging directories

Treat the sanitizer as a normal derived workload:
- `sanitize.spec` (profile + transforms)
- `sanitize.lock` (pinned toolchain + converter inputs)
- `sanitize.plan` (closure + budgets + sandbox profile)
- `sanitize.artifact` (the runnable sanitizer)

### 3) Make “sanitization” a deterministic transform lane
The output should be explainable and reproducible:
- same input + same profile + same toolchain ⇒ same output bytes (where feasible)
- non-determinism (fonts, timestamps, OCR randomness) must be policy-controlled and receipted

Integrate with existing export concepts:
- sanitized output is a derived artifact eligible for `export.policy`
- redaction transforms (if any) are separate and deterministic

### 4) Evidence objects (minimum set)
Emit a compact evidence set:
- `sanitize.receipt`:
  - input digest(s)
  - sanitizer plan digest
  - output digest(s)
  - duration + budgets used
  - any deviations from deterministic mode
  - optional consent receipt digest

Optionally add:
- `sanitize.diff` (metadata-only): e.g. page count changes, OCR enabled, image rasterization parameters

### 5) UX hooks (boring-by-default)

- `derive sanitize <file> --profile safe-pdf` (CLI)
- GUI integration: “Open safely…” context action
- policy can require sanitize-before-export for certain file classes

## Why this is worth baking in

- It turns “opening files safely” into a **standard, reviewable, cacheable** workflow.
- It aligns with DeriveBSD’s strengths: disposables, typed plans, evidence receipts, and portalized data flows.
- It provides a safe default for *humans*, not just for infrastructure.

## References

- Dangerzone project overview (render-to-pixels → rebuild safe PDF): https://dangerzone.rocks/ 
- Dangerzone repository: https://github.com/freedomofpress/dangerzone
- Dangerzone Qubes integration notes (sanitization VM pattern): https://github.com/freedomofpress/dangerzone/wiki/Qubes-OS-Integration
- Qubes disposables (stateless VM class; sanitize use-case called out): https://doc.qubes-os.org/en/latest/user/how-to-guides/how-to-use-disposables.html

Last updated: 2026-02-25
