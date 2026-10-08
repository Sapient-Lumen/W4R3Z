# Meta: Kernel Shipset Ledger Protocol

## Purpose
Use this protocol when the archive needs a compact, validated answer to:
> **what exact first shipset should a small team build for a top-ranked seam that has already earned kernelization?**

This protocol is **not** the same as:
- ranking the broad ladder,
- refreshing packet posture,
- naming a launch wedge,
- describing a decision journey,
- writing a seam-local contract,
- or widening to a program charter.

It exists for the narrower question:
> once a seam already has a worthy first build, how does the repo keep the first honest repo shape, module boundary, import surfaces, proof artifacts, and refused expansions explicit enough that future revisions do not re-invent them from memory?

Read with:
- `design/epic-contribution-kernel-shipset-ledger-2026Q1.md`
- `design/epic-contribution-v0-kernel-briefs-2026Q1.md`
- `meta/V0_KERNEL_BRIEF_PROTOCOL.md`
- `design/epic-contribution-launch-wedges-2026Q1.md`
- `design/epic-contribution-decision-journeys-2026Q1.md`
- `ledgers/top-band-kernel-shipsets-v0/shipsets.json`

## Core rule
If a revision materially changes what the archive thinks a top seam should **actually build first**, that revision should refresh both:
1. the nearest prose kernel brief; and
2. the machine-readable kernel shipset card.

If the shipset answer changes but only the prose changes, treat the revision as **first-shipset-lossy**.

## When to use this layer
Prefer the kernel shipset ledger when the user is really asking:
- what a small team should build first;
- what folders/modules/packages belong in the first repo;
- which commands or cards form the first user surface;
- what imported truths are allowed in v0;
- what proof artifacts must exist before widening the claim; or
- how to keep first-build answers aligned across multiple revisions.

## When not to use this layer
Do **not** use the shipset ledger to:
- promote a new seam into the broad ladder;
- decide that a seam deserves kernelization when it is still `hold`;
- replace a launch wedge, packet, or decision journey card;
- or claim that a passing ledger check proves the shipset is strategically sufficient.

## Required card fields
Each card in `ledgers/top-band-kernel-shipsets-v0/shipsets.json` should include:
- `shipset_id`
- `title`
- `seam`
- `status`
- `shipset_kind`
- `kernel_codename`
- `credible_home`
- `repo_modules`
- `initial_commands`
- `import_surfaces`
- `primary_journeys`
- `proof_artifacts`
- `proving_grounds`
- `maintenance_burdens`
- `refused_expansions`
- `exit_criteria`
- `related_assets`
- `supporting_sources`
- `review_horizon`
- `notes`

## Required posture
A good shipset card must:
1. stay bounded enough that a small team could plausibly own it;
2. preserve unstable / partial / caveated import posture honestly;
3. name the immediate upkeep burden;
4. link to the governing prose kernel brief and nearby launch-wedge / journey assets; and
5. keep at least one broader refused expansion visible.

## Structural non-claims
A passing `check_kernel_shipsets.py` run proves:
- the ledger parses,
- required fields exist,
- linked assets exist,
- and the required seam coverage is present.

It does **not** prove:
- the shipset is strategically correct,
- the repo modules are sufficient,
- the proving grounds are fresh,
- or the supporting sources still justify the card's exact wording.

## Default coverage rule
The kernel shipset ledger is intentionally smaller than the broad worthy-contribution map.
At the moment it should cover the seams that have already earned kernelization:
- Build-State Evidence
- Package Intake + Release Boundary Review
- Feedback / Debug Acceptance Commons
- Safety-Critical + Institutional Readiness Commons

Do not force `hold` seams into the ledger just for symmetry.

## Maintenance rule
When the ledger changes, refresh in the same revision:
- `design/epic-contribution-kernel-shipset-ledger-2026Q1.md`
- `ledgers/top-band-kernel-shipsets-v0/README.md`
- `ledgers/top-band-kernel-shipsets-v0/shipsets.json`
- `tools/check_kernel_shipsets.py`
- the nearest affected files in `kernels/top-band-v0/`
- the front-door routing and continuity rails if the default answer changed
