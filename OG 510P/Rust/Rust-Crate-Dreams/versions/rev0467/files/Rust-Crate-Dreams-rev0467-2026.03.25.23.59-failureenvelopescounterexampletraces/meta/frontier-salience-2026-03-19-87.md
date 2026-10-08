# Frontier salience snapshot — 2026-03-19 (87)

This pass did **not** add another release tool, another changelog assistant, or another generic codemod surface.
It sharpened an already-promoted lane that still remained slightly thinner than the archive’s newer support products:

- **P-0514 Crate Upgrade Pack Kit** — because Cargo, `cargo fix`, `rustfix`, `cargo-semver-checks`, release bots, and workspace metadata now provide substantial substrate, but there is still no boring receiver-facing contract for **hazard authority**, **workspace/package scope**, **follow-through coverage**, and **manual-review boundaries**.

## Main judgment

The next worthy move here was **not** another source of release facts.
Those already exist.

The sharper missing layer is the **joined upgrade-support contract** above today’s substrate, especially once three questions stay explicit:

- **hazard-authority truth** — did the hazard come from SemVer/public-API evidence, feature/default-policy drift, config/runtime policy drift, a behavior witness, or only a maintainer note?
- **package-scope truth** — did the maintained lane cover the published library crate only, or also binaries, examples, auxiliary workspace members, and non-published packages?
- **follow-through coverage truth** — did a machine fix actually cover the migration, or did it only touch Rust source while manifest/config/docs steps remained manual?

That move is better grounded now because:

- the Rust vision-doc work still calls for more supportive interfaces from crates;
- the 2025 State of Rust survey still says docs and code are the main learning surfaces;
- Cargo’s SemVer reference remains useful but intentionally conventional rather than comprehensive;
- `cargo-semver-checks` is real release substrate but still depends on unstable rustdoc JSON support windows;
- `release-plz update` explicitly integrates `cargo-semver-checks` but explicitly warns it does not catch every SemVer violation;
- `cargo release` automates release chores but does not define downstream migration lanes;
- `cargo fix` and `rustfix` are clearly source-suggestion substrate, not whole-upgrade substrate;
- Cargo external-tools / `cargo metadata --format-version` make workspace-aware import realistic;
- Cargo workspaces remain common enough that package-scope ambiguity is a practical problem, not a theoretical one;
- and the `hint-mostly-unused` write-up makes feature-flag stability language explicit enough that feature/default shifts belong inside upgrade hazard modeling.

So the gap is no longer just “release notes are vague”.
The gap is that downstream users still rarely get a **reviewable upgrade bundle** instead of folklore.

## Broad portfolio ranking after this pass

1. **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit** — still strongest because freezeable crate choice compounds many later decisions.
2. **P-0514 Crate Upgrade Pack Kit** — now much stronger because it finally distinguishes hazard authority, package scope, and follow-through coverage from generic release automation.
3. **P-0520 Crate Lifecycle Surface Pack Kit** — still unusually strong because start/stop truth remains widely missing.
4. **P-0522 Crate Persistence Surface Pack Kit** — still one of the sharpest support-surface lanes now that persisted-state promises are specific.
5. **P-0521 Crate Resource Surface Pack Kit** — still strong because admission and waiting-room truth are concrete.
6. **P-0524 Crate Example Surface Pack Kit** — still a high-leverage first-success lane.
7. **P-0523 Crate Test Surface Pack Kit** — still high-leverage because support-level truth and witness lineage are concrete.
8. **P-0519 Crate Authority Surface Pack Kit** — still strong because origin, fallback, and refusal behavior are explicit.
9. **P-0518 Crate Observability Surface Pack Kit** — still strong because route truth and sensitivity boundaries remain under-supported.
10. **P-0512 Crate Guidance Pack Kit** — still strong because message/channel/env truth remains under-published.

## Why this beat nearby lanes this round

Several nearby lanes are still good.
But this one won because it compounds **at release edges**, where maintainers and adopters already have fresh attention.

If a crate release can now be versioned, changelogged, semver-checked, and maybe partially auto-fixed, the next missing leverage is not more publication ceremony.
It is the small artifact that says what a downstream upgrader actually has to do, what evidence backs that claim, and what still needs a human.
