# ADR-0300: Breakglass adapter details stay redacted side evidence and off baseline receipt

- Status: Accepted
- Date: 2026-03-23

## Context

`ADR-0296` through `ADR-0299` already narrowed the breakglass authority story substantially:

- the session method is concrete (`console`, `serial`, `ssh`),
- pre-session recovery history joins through exact `boot.override.receipt` / `reset.receipt` digests,
- plural bootstrap joins stay enabling-only and causally ordered,
- and the common paired one-time-boot path is `boot.override.receipt` then `reset.receipt`.

That leaves one nearby seam still expensive to leave fuzzy:

**what, if anything, belongs in the baseline breakglass receipt about the remote-presence adapter itself?**

Real management stacks expose a lot of adapter-specific detail:

- Redfish distinguishes graphical console, serial console, and virtual media rather than one generic OOB shape.
- Serial-console surfaces can publish connection-specific client hints such as `ConsoleEntryCommand` and `HotKeySequenceDisplay`.
- Virtual media can involve browser proxy mode, BMC-managed remote image mounting, or other implementation-specific transport details.
- Vendor consoles add plugin/runtime choices, session limits, crash-video capture, launch affordances, and other UI/runtime artifacts.

Those details are operationally useful, but they are not the same thing as the portable authority story.
They also vary sharply by adapter/vendor and often carry locator, launch, or session detail that should not silently become routine support/export truth.

If the archive leaves this seam vague, implementations will be tempted to widen `breakglass.receipt` with BMC URLs, launch files, console ports, session ids, image locators, or ticket prose inside `notes`.
That would turn a portable authority receipt back into adapter folklore.

## Decision

1. The baseline portable breakglass receipt stays **adapter-thin**.
   Its reviewed authority story is still:
   - concrete `session.method`
   - exact bootstrap receipt joins when pre-session recovery materially enabled entry
   - exact TTY recording joins when the stronger interactive evidence lane participated
   - exact `repair_outcome.authoritative_receipt_digests` for post-entry repair truth

2. Adapter-specific runtime detail does **not** get first-class baseline receipt fields in v0.
   This includes examples such as:
   - vendor/product-specific BMC console metadata
   - remote console launch URLs or ports
   - session ids, cookies, or tokens
   - `ConsoleEntryCommand` / hotkey text copied from a management API
   - virtual-media image locators or browser/WSS/CIFS/HTTPS mode details
   - screenshots, crash-video captures, or dashboard breadcrumbs

3. If those adapter details are captured at all, they remain **redacted side evidence** under explicit export/support policy rather than baseline `breakglass.receipt` truth.
   They may later earn a dedicated evidence artifact family or support-bundle convention, but that must be a separate RFC/ADR cut.

4. `breakglass.receipt.notes` is not a loophole for smuggling adapter secrets or locators back into the canonical receipt.
   Notes stay operator summary text, not launch-data storage.

## Consequences

Good:

- the portable breakglass receipt stays coherent across A/B/C/D without minting a premature adapter taxonomy,
- support/export posture stays aligned with the archive's broader digest-first / stronger-side-evidence discipline,
- privacy and secret-spill risk stay lower because live adapter/session detail is not normalized into the baseline receipt,
- and future richer adapter work can be RFC-first instead of arriving as accidental schema growth.

Costs:

- readers who need exact adapter runtime detail must fetch a stronger explicit side-evidence lane instead of assuming the baseline receipt carries everything,
- schema/docs need one more explicit sentence that `notes` is not an adapter-detail escape hatch,
- and any future dedicated adapter artifact family must define its own redaction/export posture instead of inheriting it implicitly from breakglass.

## Follow-on

Still open as implementation detail:

- whether a dedicated adapter-side-evidence artifact family is worth standardizing,
- how incident/support bundles should point at richer adapter artifacts when they materially matter,
- and which redacted adapter hints, if any, deserve a cross-vendor review UI without turning launch/runtime data into routine exported truth.
