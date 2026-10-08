# VHK / VisualHotKey

## A recorded action must meet the desktop that actually exists

VHK is an AHK-shaped desktop automation project whose later source snapshots focus on i3/X11 and a session-bound resident service. Its central loop is recording, cleaning up, replaying, inspecting and refining a macro.

The interesting difficulty is not simply replaying keystrokes. A previously successful macro may belong to a different window state, desktop session, source contract or daemon instance. A receipt has to describe the thing being trusted now, not merely remember that something once worked.

## Read a source snapshot before the final carrier

1. Start with [the rev0412 product stance](versions/rev0412/files/VHK-rev0412-2026.03.22.03.18-proofwriter-signoffhelper-ledgerflow-currentacceptance/README.md). It ties replay and acceptance to the current macro and session rather than treating an older signoff as permanently current.
2. Compare [the later runtime-instance account](versions/rev0511/files/README.md). Its repeated efforts to align live state, repair history and the concrete resident service show which forms of stale evidence the project is trying to avoid.
3. Use the earlier version shelf to follow changes in scope and authoring tools.
4. Read [rev0575’s bootstrap prose](versions/rev0575/files/BOOTSTRAPROSE.md) as the documentation accompanying a different artifact form. That delivery contains the prose and an ELF executable carrier. The carrier is preserved, not run or presented here as a fully inspected source tree.

## What the narrower platform choice buys—and does not buy

Focusing on i3/X11 makes the intended desktop and runtime contract more specific. It does not automatically qualify a different display server, desktop environment or current machine. Nor does a machine-readable next-action surface prove that the chosen action is appropriate for a person’s present task.

The historical authoring and execution instructions are part of the design. This edition records no live replay, installs no service and grants no model access to a desktop.

Read beside [GlassTTY](../GlassTTY/README.md) for a browser-oriented control surface and [Sandcodex](../../guides/Sandcodex.md) for a separately maintained project room with explicit authority choices.

*Reading introduction by Lumen, 8 October 2026. These are selected historical works; their software, experiments and maintenance instructions have not been activated by this edition.*

## Version shelf and preservation

## Reading order

Start with the newest selected snapshot for its entry points and stated limits; compare earlier snapshots for changes. These are selected deliveries, not an assertion of a complete revision history.

- [rev0016](versions/rev0016/README.md): 132 preserved members; `vhk_repo_rev0016.tar.gz`.
- [rev0108](versions/rev0108/README.md): 250 preserved members; `VHK-rev0108-2026.03.05.05.01-oscd-oscudp-controllerglue-pegasus.zip`.
- [rev0205](versions/rev0205/README.md): 466 preserved members; `VHK-rev0205-2026.03.08.15.58-systemdunitstates-serviceorchestration-unitbeacon.zip`.
- [rev0313](versions/rev0313/README.md): 652 preserved members; `VHK-rev0313-2026.03.17.23.59-incidentdrift-historysignals-recoverytruth-pineharbor.zip`.
- [rev0412](versions/rev0412/README.md): 829 preserved members; `VHK-rev0412-2026.03.22.03.18-proofwriter-signoffhelper-ledgerflow-currentacceptance.zip`.
- [rev0511](versions/rev0511/README.md): 1,063 preserved members; `VHK-rev0511-2026.03.28.13.29-repairinstanceproof-witnessalignment-x11lane.zip`.
- [rev0575](versions/rev0575/README.md): 2 preserved members; `VHK-rev0575-2026.08.22.19.06-renamenoreplace-waitstreamretirement-raceclosed.zip`.

[Original identities](PROVENANCE.json) · [Back to OG 510P](../README.md)
