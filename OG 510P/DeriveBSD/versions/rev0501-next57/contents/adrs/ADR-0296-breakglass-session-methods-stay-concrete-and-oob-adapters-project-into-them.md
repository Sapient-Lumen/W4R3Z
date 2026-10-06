# ADR-0296: Breakglass session methods stay concrete and OOB adapters project into them

- Status: Accepted
- Date: 2026-03-23

## Context

`docs/236-breakglass-and-recovery-mode.md`, `docs/250-breakglass-and-recovery-workflows.md`, and `docs/618-breakglass-recording-detail-and-export-posture-by-profile.md` already fixed the big breakglass questions:

- breakglass is an explicit lease-shaped emergency lane,
- the recording/detail/export posture is profile-shaped,
- interactive shell/console evidence starts at session open before the first prompt,
- and breakglass closeout now carries typed `repair_outcome` truth.

But one smaller authority seam stayed fuzzy in the schemas:
`breakglass.grant.scope.allowed_methods` and `breakglass.receipt.session.method` still allowed `oob`.

That is too vague to be a stable implementation target.
“Out-of-band” can describe several *different* things:

- approval transport,
- BMC/remote-presence console projection,
- serial-over-LAN,
- virtual-media boot into a recovery image,
- or other pre-session maintenance plumbing.

If the archive leaves that bucket unshaped, very different mechanisms collapse into one authority noun. That makes evidence, profile defaults, and later adapter work harder to reason about across A/B/C/D.

## Decision

1. Breakglass access/session methods stay **concrete**.
   The first reviewed method vocabulary is:
   - `console`
   - `serial`
   - `ssh`

2. `oob` is **not** a breakglass session method.
   It may still describe approval transport or maintenance ceremony elsewhere in the archive, but it does not belong on the breakglass access-surface vocabulary.

3. Remote-presence adapters project into concrete methods instead of minting new authority kinds.
   - BMC KVM / HTML5 console projects to `console`
   - Serial-over-LAN projects to `serial`
   - a recovery image reached through virtual media stays adapter/bootstrap plumbing until it yields an actual `console`, `serial`, or `ssh` breakglass session

4. If a future lane needs richer adapter-visible evidence, it should arrive as an explicit follow-on cut.
   This ADR does **not** standardize the full per-adapter evidence schema.

## Consequences

Good:

- breakglass authority stays legible and implementable,
- OOB approvals remain valid without being confused with access-surface truth,
- BMC / virtual-media / serial-console work can stay adapter-shaped instead of forking the breakglass noun set,
- and support/export surfaces can answer “what concrete session surface was used?” without hiding behind a catch-all bucket.

Costs:

- schema text must distinguish approval transport from access method,
- and future adapter detail work must earn its own narrow follow-on cut instead of smuggling itself in through `oob`.

## Follow-on

Still open as implementation detail:

- whether richer adapter/runtime detail deserves a dedicated side-evidence artifact family now that `ADR-0300` keeps the baseline breakglass receipt adapter-thin,
- how much pre-session virtual-media/bootstrap state deserves first-class support-bundle joins,
- and which recovery UX affordances should render redacted adapter provenance prominently.
