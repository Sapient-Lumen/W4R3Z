
# Frontier salience snapshot — 2026-03-19 (86)

This pass did **not** add another ranking engine, another general ecosystem dashboard, or another de facto standard-library proposal.
It sharpened a lane that has remained strategically central across the whole archive:

- **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit** — because Cargo, crates.io, docs.rs, and official Rust guidance now expose more signals than before, but teams still lack one boring receiver-facing contract for **starter-set readiness**, **lock-in cost**, **scope split**, **evidence origin**, and **freeze boundaries**.

## Main judgment

The next worthy move here was **not** another signal source.
Those already exist.

The sharper missing layer is the **joined ecosystem decision contract** above today’s substrate, especially once three facts stay explicit:

- **starter-set readiness truth** — whether a candidate stack is actually ready to freeze, still hides required companion crates, still needs more maturity time, or still requires manual review,
- **lock-in-cost truth** — where runtime choice, proc-macro usage, trait adoption, configuration style, companion crates, or ecosystem gravity make exit expensive,
- **scope-split truth** — when teaching defaults, production defaults, org-policy defaults, and niche target defaults overlap versus intentionally diverge.

That move is better grounded now because:

- the Rust vision-doc work explicitly says users still struggle with **which crates to use** and that there is no clear starter set;
- the 2025 State of Rust survey still says docs and code are the main learning surfaces, which raises the leverage of boring default decisions;
- `cargo search`, `cargo add`, and `cargo info` all help, but all still assume the team is already fairly close to a choice;
- Cargo’s stable external-tools surfaces make it realistic to build a decision crate above existing workflows rather than against them;
- crates.io has added security and publishing signals that are useful imports but not a task-lane decision in themselves;
- docs.rs target/default-target behavior is now legible enough that visible support claims can be imported, but still not scoped automatically to teaching versus production.

So the gap is no longer “there are too many crates”.
The gap is that teams still rarely get a **reviewable freezeable crate-choice bundle** instead of oral tradition.

## Broad portfolio ranking after this pass

1. **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit** — now stronger because it finally distinguishes ranking from freeze readiness and teaching defaults from production defaults.
2. **P-0520 Crate Lifecycle Surface Pack Kit** — still unusually strong because start/stop truth is widely missing.
3. **P-0522 Crate Persistence Surface Pack Kit** — still one of the sharpest support-surface lanes now that persisted-state promises are specific.
4. **P-0521 Crate Resource Surface Pack Kit** — still strong because admission and waiting-room truth are concrete.
5. **P-0524 Crate Example Surface Pack Kit** — still a high-leverage first-success lane.
6. **P-0523 Crate Test Surface Pack Kit** — still high-leverage because support-level truth and witness lineage are concrete.
7. **P-0519 Crate Authority Surface Pack Kit** — now stronger because origin, fallback, and refusal behavior are explicit.
8. **P-0512 Crate Guidance Pack Kit** — now stronger because early-failure support is framed as message/channel/env truth rather than vague “better errors”.
9. **P-0518 Crate Observability Surface Pack Kit** — still strong because route truth and sensitivity boundaries remain under-supported.
10. **P-0525 Crate Diagnosis Surface Pack Kit** — still strong because symptom identity and safe capture remain under-documented.

## Why this beat nearby lanes this round

Several nearby lanes are still good.
But this one won because it compounds **before** most other choices.

If Rust users still cannot confidently choose or freeze a starter set, then many downstream support-surface improvements arrive too late.
A pathfinder/decision-pack crate can improve onboarding, internal platform policy, teaching materials, architecture reviews, and later migration planning all at once — *provided* it stops pretending that popularity rank alone is the answer.
