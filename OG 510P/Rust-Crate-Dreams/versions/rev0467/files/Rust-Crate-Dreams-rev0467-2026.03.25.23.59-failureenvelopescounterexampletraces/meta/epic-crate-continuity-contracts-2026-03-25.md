# Epic crate continuity contracts — 2026-03-25

This note extends the archive’s earlier adoption-contract lens.

A crate can be impressive at intake time and still fail the deeper test.
A more worthy crate is one that remains useful **after the first decision**.

That is the continuity-contract test.

## Definition

A **continuity contract** is the part of a crate’s value proposition that answers:

- how earlier outputs stay reviewable,
- what signals reopen them,
- what can be imported automatically,
- what must be re-judged manually,
- how drift is rendered,
- and how the receiver can safely move from “keep” to “change” without losing history.

## Why it matters

The Rust ecosystem is now rich enough that many teams do not mainly need “more crates”.
They need help managing:
- multiple candidates,
- partial evidence,
- target variability,
- support drift,
- registry/mirror differences,
- policy changes,
- and later replacement pressure.

That is where an epic crate contribution can create institutional leverage.

## Ten continuity questions every worthy crate should answer

1. **What earlier artifact does this output inherit?**
2. **What new trigger or signal reopened the question?**
3. **Which parts of the answer are freshly observed, and which are carried forward?**
4. **Which imported substrates does this crate trust?**
5. **What changed category: docs, build, target, security, source, boundary, policy, or lifecycle?**
6. **What is the support ceiling after the change?**
7. **What stayed true from the older answer?**
8. **What transition paths exist: keep, pin, except, re-evaluate, migrate, replace, or retire?**
9. **What exact artifact should another reviewer read next?**
10. **What does the crate explicitly refuse to claim?**

## What a `0.1` continuity contract should contain

A first useful release does not need to solve everything.
It should still contain:

- one **carry-forward mechanism**
- one **trigger intake** route
- one **diff category** vocabulary
- one **transition artifact**
- one **support ceiling** vocabulary
- and one **rendered summary** a teammate can understand without reading internal code

## Imported frameworks and substrate

A worthy continuity-oriented crate should prefer imported substrate over invented truth.
It should lean on real surfaces such as:
- crates.io security/trust/timing posture,
- docs.rs metadata/download/rustdoc JSON/build facts,
- Cargo machine-usable reporting surfaces,
- semver/public-boundary evidence,
- and target/toolchain/component support inputs.

The crate’s distinctive value is not replacing those systems.
It is joining them into a receiver-usable contract.

## Test corpus expectations

A continuity-oriented crate should ship scenarios that prove it can survive:
- a new advisory with no migration yet,
- a mirror/offline route with partial degradation,
- a public-boundary widening,
- a docs.rs hosted/local mismatch,
- a target-support downgrade,
- a planned replacement,
- and a “nothing important changed” recheck.

## Theory / practice split

### In theory
A continuity contract is a stable vocabulary for carrying decisions forward.

### In practice
A continuity contract is:
- JSON reports,
- short markdown summaries,
- imported source locators,
- and an explicit refusal boundary.

If a proposal cannot say what those files are, it is not yet planned tightly enough.

## Archive consequence

Future passes should not describe a crate as “epic” merely because the problem is large.
They should ask whether the crate would reduce repeated institutional memory loss for real downstream teams.
