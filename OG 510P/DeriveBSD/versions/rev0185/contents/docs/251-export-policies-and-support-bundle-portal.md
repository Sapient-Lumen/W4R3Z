# Export policies + support-bundle portal

DeriveBSD already has **incident/support bundles** (`docs/216-incident-snapshots-and-support-bundles.md`) and **deterministic redaction transforms** (`docs/195-deterministic-redaction-transforms.md`).

The missing groundfloor feature is: **a first-class, user-/policy-mediated export path**.

Older ecosystems often treat "collect diagnostics" as one tool, and "send it to someone" as an ad-hoc follow-up (scp the tarball, paste logs, attach it to a ticket). That breaks least-authority and makes it hard to prove what was shared.

This doc introduces:
- `export.policy`: a *share contract* (what may be exported, to whom, and with what transforms)
- `export.receipt`: evidence that an export occurred (with policy + transforms + recipients)
- a **Support Bundle Export Portal**: a portal-shaped UI/UX that binds consent + routing to the policy surface
- `transport.policy` + `transport.receipt`: transport adapters as a policy-bound lane (`docs/255-policy-constrained-transports.md`).
- `consent.request` + `consent.receipt`: a uniform approval/consent contract across GUI/TTY/OOB (`docs/256-consent-ux-contract.md`).
- `export.transparency.entry`: optional append-only logging of export events (`docs/254-export-transparency-logs.md`).

## Goals

- Make every export **reviewable** (policy as data) and **auditable** (receipt as evidence).
- Keep exports **least-authority**: exporting is not equivalent to "root can read everything".
- Make bundle sharing **reproducible**: two parties can verify they are looking at the same exported bytes.
- Integrate cleanly with existing lanes:
  - incident bundles
  - tracing outputs
  - crash artifacts
  - redaction transforms
  - leases and breakglass

## Non-goals

- This does *not* define a specific transport (email, upload, pastebin, ticket system). The export path is a **pluggable adapter**, constrained by `transport.policy` (`docs/255-policy-constrained-transports.md`).
- This does *not* require a GUI. The portal model can be implemented as:
  - GUI prompt
  - TTY prompt with secure attention
  - OOB approval flow

## Prior art to steal

- **XDG Desktop Portal** model: sandboxed apps request a mediated capability and get a handle (not raw filesystem access). The FileChooser and FileTransfer portals are concrete examples of "user-mediated export" in practice.
  - FileChooser: https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.portal.FileChooser.html
  - FileTransfer: https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.portal.FileTransfer.html
- **sosreport** operational lesson: collect a standard bundle for support, but treat it as sensitive; shipping it is a distinct action.
  - RHEL sos report docs: https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/8/html-single/generating_sos_reports_for_technical_support/index

## Key idea

In DeriveBSD, "export" is a **separately authorized step**:

1. A bundle exists (or is produced) as a content-addressed artifact.
2. A policy allows exporting *this class of artifact* to *this class of recipient*.
3. A lease authorizes this export attempt (portal grant or breakglass grant).
4. The export runs through an adapter and produces an `export.receipt`.

## Artifact boundaries

### `export.policy` (new)

A policy object that declares:
- allowed artifact kinds (incident bundles, trace outputs, crash reports, …)
- mandatory transforms (redaction transform digests, field drops)
- destination constraints (recipient identities, ticket ids, allowed transports)
- whether **interactive consent** is required (portal)
- whether **two-person approval** is required
- encryption requirements (age/PGP/CMS)

See: `spec/export.policy.schema.json`.

### `export.receipt` (new)

Evidence that an export occurred, including:
- exported artifact digest(s)
- policy digest
- redaction transform digest (if applied)
- lease id used to authorize the export (if any)
- transport adapter metadata (destination, upload id, ticket id)

See: `spec/export.receipt.schema.json`.


## Related evidence objects (optional but recommended)

Exports often cross trust boundaries. For high-assurance deployments, prefer emitting:
- `consent.receipt` (who approved the export, and how)
- `transport.receipt` (where the bytes went, metadata-only)
- `export.transparency.entry` (append-only log record + inclusion proof)

These digests may be embedded into `export.receipt` and referenced from incident bundles.

Schemas:
- `spec/consent.receipt.schema.json`
- `spec/transport.receipt.schema.json`
- `spec/export.transparency.entry.schema.json`

## Support Bundle Export Portal (concept)

A portal call takes:
- `bundle_digest` (incident bundle payload digest or a logical bundle id)
- `export_policy_digest`
- `recipient` (or recipient class) + `ticket_id`
- optional `requested_transform_digest` (must be permitted by policy)

It returns:
- a **timeboxed lease** authorizing the export attempt
- a **receipt digest/id** after completion

This mirrors portal ergonomics: request capability → get scoped handle → perform action.

## How this composes with breakglass

Breakglass grants already include `export-support-bundle` as an allowed op.
In DeriveBSD, breakglass does *not* bypass export policy:
- breakglass may enable the *portal path* (or a CLI path) to be used in recovery mode
- export still produces an `export.receipt`
- export policy still defines transforms and destination constraints

## Operational guidance

- Default export policy for external vendors should:
  - forbid raw core/kernel dumps
  - require redaction transforms
  - require encryption
  - require ticket id
- Provide a `bundle-min` mode (see `docs/246…` + `docs/253…`) so exports are small and explainable.

