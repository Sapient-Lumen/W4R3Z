# Frontier salience snapshot — 2026-03-21-142

This pass did **not** add another derive macro, another pretty renderer, or another CLI-only reporting helper.
It added **P-0533 Error Surface Contract Kit**.

## Why this frontier moved up

The current Rust substrate now makes the gap unusually concrete:

- `std::error::Error` gives the ecosystem a shared base around `Display`, `Debug`, `source()`, and an experimental typed-context `provide()` hook;
- `thiserror` explicitly aims to stay out of public API branding, which is useful but means it does not itself publish a downstream-facing compatibility contract;
- `anyhow` optimizes for ergonomic application context layering;
- `miette` and `ariadne` make rich diagnostics and help text practical;
- `error-stack` and `snafu` make reports, attachments, chains, and backtraces practical;
- and the 2025 State of Rust survey says many users do find compiler error-code explanations useful while debugging remains one of the major productivity problems.

That combination means the missing crate is not another error stack implementation.
It is a **receiver-facing contract** that can publish **error identity**, **audience mode**, **remediation surface**, and **sensitivity posture** above today’s error crates.

## Main conclusion

Promote **P-0533** quickly, but keep it narrow.
The next worthy move is not another universal error type and not another terminal renderer.

It should stay focused on:

1. freezing which error identities are actually stable,
2. separating human, operator, developer, and machine surfaces,
3. making help/retry/docs posture explicit instead of ornamental,
4. keeping backtrace/attachment/snippet sensitivity visible,
5. and letting teams diff error-support posture across releases and modes.

## Ranked near-term frontier from this pass

1. **P-0533 Error Surface Contract Kit** — strengthened because the substrate for error construction is rich, but exported support posture is still implicit.
2. **P-0531 CLI Surface Contract Kit** — still strong because stdout/stderr/exit semantics remain adjacent but distinct from error identity/remediation/sensitivity.
3. **P-0525 Crate Diagnosis Surface Pack Kit** — still strong because first-diagnosis workflow remains separate from steady-state error contracts.
4. **P-0004 Diagnostic Kit** — still relevant as a renderer/data-model lane, but it should not absorb the new contract layer.
5. **P-0017 Trust Lens** — still strong because sensitive exported errors often feed trust and review workflows, but trust-watch posture is a separate lane.

## Keep these boundaries sharp

- **P-0533** is error identity + audience mode + remediation surface + sensitivity posture.
- **P-0004** is diagnostic rendering and data-model ergonomics.
- **P-0531** is command/output/terminal/exit behavior.
- **P-0525** is first-diagnosis guidance and self-check bundles.
- broader secrets/redaction lanes remain separate from error-specific exposure truth.

Do not let “good error handling” flatten those lanes into one fake crate.
