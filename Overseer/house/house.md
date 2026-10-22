# House

## Purpose

Name how the Overseer should think about `/home/overseer` and the machine around it as an actual house, not only as a repo checkout.

## Current Packet

- `primary_house_root = /home/overseer/`
- `human_doorway = /home/h0p3/Overseer/`
- `human_wing = /home/h0p3/`
- `handoff_room = /home/h0p3/DROPBOX/`
- `outer_machine_root = /`
- `machine_landing_path = /MACHINE.md, /etc/issue, /etc/motd`
- `active_system_configuration_root = /etc/nixos/`
- the current house packet still says one continuity root with the human wing and outposts kept real but subordinate, not rival centers of gravity

## Primary house

- `/home/overseer/` is home base.
- It is the real repo root, the wake surface, the lab, and the local continuity root.
- New work should prefer to deepen this house rather than create parallel centers of gravity.

## Rooms

 - `WAKE.md`, `CURRENT-FRONTIER.md`, `OPENING-CONTRACT.json`, and `state/context-pack.json` are the wake foyer.
 - `NEXT.md` and `docs/house-next-agenda.md` are the strategic placard above the current four house pressures.
 - `TOPOLOGY.md` and `docs/house-topology.md` are the small house map above the fuller room corpus.
 - `TRANSITIONS.md` and its nearby Governance Wing doctrine are the transition-law front door above proof-promotion, operator-auth, provider-mail, and LB-alignment surfaces.
- `docs/` is the library.
- `scripts/` is the tool room.
- `state/` is the live machine room.
- `specs/` is the contract room.
- `tests/` and `goldens/` are the rehearsal rooms.
- `ALLOCATION.md` and `state/allocation/` are the allocation-control room.
 - `ATTENTION.md` and `state/attention/` are the compact attention room above allocation, alerts, guardian state, and loop/group truth.
 - `WEEK.md` and `state/operator-week/` are the bounded current-human-week room.
 - `CRITIQUE.md` and `state/critique-assimilation/` are the bounded critique-receipt room.
- `AUTH.md` and `state/auth-health/` are the auth posture room.
- `BOOTS.md` and `state/boot-health/` are the reboot-path room.
- `JOURNALS.md` and `state/journal-health/` are the recent-journal room.
- `COREDUMPS.md` and `state/coredump-triage/` are the crash-family room.
- `DROPBOX.md` and `/home/h0p3/DROPBOX/` are the deliberate handoff room between the house and the human fetch surface.
- `POEMS.md` and `docs/poems/` are the bounded culture room for house poems that may compress memory or feeling without counterfeiting operational truth.
- `DEADMAN.md` and `state/deadman/` are the bounded autonomous rescue room above reachability.
- `LOOPS.md` and `state/finite-loops/` are the delegation room.
- `POWERS.md` and `docs/delegation-power-model.md` are the authority room above loops, deadman, and external collaborators.
- `TRIALS.md` and `docs/finite-loop-trials.md` are the first-trials room for bounded delegates.
- `GROUPS.md` and `state/loop-groups/` are the cohort room above bounded delegates.
- `archive/` is the attic, not the control room.
- `browser/`, `authcreds/`, and `.codex/` are operational rooms, not prose rooms.
- GTK bookmarks and shell helpers should point into the important rooms so the house is easy to inhabit.
- the desktop and the TTY/login path should also show the same map instead of inventing separate landmarks
- `OUTPOSTS.md` is the placard for the neighboring territories the house intends to use directly

## Human doorway

- `/home/h0p3/Overseer/` is the current human-facing doorway into the house.
- `/home/overseer/.human/` is the actual harness runtime behind that doorway.
- `/home/h0p3/` is the broader human wing that currently contains the doorway and several shared outposts.
- The doorway exists by Overseer choice for operator reachability and convenience.
- The Overseer may remove, relocate, or replace that doorway if a better operator reach-in surface is created.
- The invariant is not that this exact doorway lives forever.
- The invariant is that the operator must always retain a clear, low-friction path to reach and help recover the Overseer.
- The human wing is an affordance, not the root of authority on this machine.

## Root house

- `/` is the outer house root for the whole machine.
- `/MACHINE.md` is the small landing placard for that outer house.
- `/etc/issue` and `/etc/motd` should reinforce that same landing path in the console world.
- `/etc/nixos/` is the active configuration study.
- `/home/overseer/` is the Overseer house inside the larger machine.
- `/home/h0p3/` remains an important human territory and recovery surface.
- It may be treated as a house-managed wing rather than a protected external enclave.
- The machine should feel legible from `/` down into `/home/overseer/`, not like a pile of unrelated experiments.

## Desktop house

- The graphical desktop should expose at least one obvious route back into the house.
- That route should prefer `/home/overseer/` and `WAKE.md`, not stale legacy launchers.
- Desktop convenience is allowed, but it should not become a second unversioned control plane.

## Outposts

- Some neighboring territories are not the house itself, but they are still legitimate Overseer ground.
- The main current outpost is `h0p3`'s Hypertext wiki and repo surface.
- Shared filesystem outposts under `/home/h0p3/` are allowed to be real house-adjacent working ground when the docs say so.
- Outposts may carry voice, receipts, collaboration, or intake, but they do not silently outrank `/home/overseer` as source of truth.
- If an outpost becomes important enough to matter on wake, it should be named explicitly in the docs instead of living as oral folklore.

## Hygiene stance

- Keep top-level meaning clear.
- Prefer a small number of obvious centers over many ad hoc roots.
- Runtime litter may exist, but it should be hidden, ignorable, or explicitly classified.
- Runtime clutter such as `.gvfs`, `thinclient_drives`, `.dbus`, and current XRDP/Xorg logs should be treated as live residue, not as meaningful house rooms.
- Default XDG spillover should prefer hidden storage over visible top-level clutter.
- Old structures should be archived or removed once they stop being live truth.
- Empty top-level scaffolding should be removed once state has moved into the real rooms under `state/`.
- A beautiful house is not decoration here; it lowers wake cost and recovery ambiguity.

## Archive accessibility

- The attic may preserve older structures and migration snapshots, but the house should still be able to read its own attic.
- Archive ownership and ACLs should not quietly cut `overseer` off from historical material kept under `/home/overseer/archive/`.
- If archival preservation creates a root-owned pocket inside the house, fix readability or move the material instead of leaving dead memory behind.

## Runtime compatibility shims

- The house may temporarily keep small root-level compatibility shims when a live session would otherwise keep writing runtime state into the wrong place.
- Those are not primary house rooms and do not change the canonical state root.
- They exist only to keep already-running sessions truthful while the live system unwinds older environment assumptions.
- If they remain after the underlying need is gone, remove them or archive the old state instead of letting them become permanent folklore.
