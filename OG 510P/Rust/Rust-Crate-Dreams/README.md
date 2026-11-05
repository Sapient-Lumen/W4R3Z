# Rust-Crate-Dreams

## A worthwhile tool should tell you where its promise breaks

Rust-Crate-Dreams is an idea bank for missing crates and tools. The selected revision brings disproof into the proposed deliverable: a useful contribution should help a downstream team understand a failing scenario, the witness that defeats a claim, the narrower guarantee that survives and what might repair the gap.

That moves the project beyond a wish list. The question becomes what another person would actually receive, inspect and rely on when adopting the proposed tool.

## Read one proposed failure boundary

1. Open [the supplied overview](versions/rev0467/files/Rust-Crate-Dreams-rev0467-2026.03.25.23.59-failureenvelopescounterexampletraces/README.md) and [the human index](versions/rev0467/files/Rust-Crate-Dreams-rev0467-2026.03.25.23.59-failureenvelopescounterexampletraces/INDEX.md).
2. Read [the failure-envelope note](versions/rev0467/files/Rust-Crate-Dreams-rev0467-2026.03.25.23.59-failureenvelopescounterexampletraces/meta/frontier-failure-envelopes-2026-03-25.md). One of its examples concerns differences between local and hosted documentation/build evidence: a local success is not automatically evidence for the hosted claim a receiver cares about.
3. Follow the [Docs.rs Build Parity & Evidence Kit](versions/rev0467/files/Rust-Crate-Dreams-rev0467-2026.03.25.23.59-failureenvelopescounterexampletraces/proposals/docsrs-build-parity-evidence-kit.md) from a maintainer's problem to its proposed output, then read the [later falsification plan](versions/rev0467/files/Rust-Crate-Dreams-rev0467-2026.03.25.23.59-failureenvelopescounterexampletraces/meta/top-lane-falsification-plans-2026-03-25.md) to see how the output would narrow a downstream claim.

## From a local success to an inspectable failure

A crate maintainer can obtain clean local documentation and still face a failed hosted build. The Docs.rs evidence-kit proposal starts with that practical mismatch. Its intended product is a compact bundle that another maintainer can compare, attach to an issue or carry into release review, rather than another renderer or a promise of perfect emulation.

The bundle separates three questions. **What configuration was effective?** Targets, features, compiler and documentation flags belong beside the toolchain identity. **What kind of attempt supplied the result?** Metadata inspection, a local preflight, reproduction in the builder environment and an imported hosted result have different reach. **What explains a disagreement?** A diff should retain the observations and identify candidate causes without promoting an inference into an observed fact. The proposed fidelity report makes the second question explicit instead of letting a green local result speak for every environment.

There are concrete reasons for these distinctions. The [official docs.rs build guidance](https://docs.rs/about/builds) says its `docsrs` configuration applies to the final rustdoc invocation, not to dependencies, and distinguishes it from the `DOCS_RS` signal available to build scripts. It also describes a read-only source tree and blocked network access. A local attempt with writable sources or a needed download available can therefore leave a hosted assumption untested. The proposal's fixture families turn those differences into things to investigate: capture the effective configuration, preserve the relevant failure and carry the smallest useful comparison to the next reader. These are specified test cases, not reported successful reproductions.

The March 25 plan pairs this proposal with P-0484 to supply documentation- and target-related failure evidence: an envelope names the affected claim, a counterexample trace shows what defeats it, and a repair hint points to a smaller replay. Crucially, a documentation failure in one environment does not establish that the crate fails at runtime everywhere. A downstream recommendation might withdraw hosted-documentation confidence while retaining a narrower supported claim. The useful handoff is the reason for that change, not a red badge detached from its scope.

This gives the idea bank a concrete design test: can one small contribution make another team's next decision better informed without requiring them to adopt a whole platform?

## What a successful send actually promises

The portfolio also asks how to make already-existing concurrency primitives easier to use honestly. [P-0538, Concurrency Contract Kit](versions/rev0467/files/Rust-Crate-Dreams-rev0467-2026.03.25.23.59-failureenvelopescounterexampletraces/proposals/concurrency-contract-kit.md), proposes a small reporting layer above libraries such as Tokio, rather than a replacement channel or runtime. A reader should be able to distinguish queue admission, eventual observation, processing acknowledgment, cancellation effects and shutdown without compressing them into one “safe” label.

Its [mpsc acceptance example](versions/rev0467/files/Rust-Crate-Dreams-rev0467-2026.03.25.23.59-failureenvelopescounterexampletraces/fixtures/concurrency-contract-kit/scenarios/tokio_mpsc_send_ok_means_receiver_open_not_eventual_receipt/delivery-acceptance.report.example.json) records what a successful send establishes and what it does not. Tokio's [sender documentation](https://docs.rs/tokio/latest/tokio/sync/mpsc/struct.Sender.html#method.send) explicitly allows the receiver to disappear after success, before receiving the value. The [broadcast example](versions/rev0467/files/Rust-Crate-Dreams-rev0467-2026.03.25.23.59-failureenvelopescounterexampletraces/fixtures/concurrency-contract-kit/scenarios/tokio_broadcast_send_count_is_hint_not_observation_receipt/observation-evidence.report.example.json) makes a neighboring distinction: an active-receiver count is not a receipt from those receivers. The [official broadcast contract](https://docs.rs/tokio/latest/tokio/sync/broadcast/struct.Sender.html#method.send) also allows subscribers to drop or lag before observation. A team needing proof of processing must arrange an acknowledgment with that meaning.

The carried history explains why this became a proposal rather than just a comparison chart. [Entry 428](versions/rev0467/files/Rust-Crate-Dreams-rev0467-2026.03.25.23.59-failureenvelopescounterexampletraces/entries/2026-03-23-428.md) adds acceptance and observation evidence; [entry 432](versions/rev0467/files/Rust-Crate-Dreams-rev0467-2026.03.25.23.59-failureenvelopescounterexampletraces/entries/2026-03-23-432.md) separately asks who owns the progress cursor and whether one slow receiver changes another's situation. These are different engineering questions. Receiving the latest shared state, competing for one queued job and independently following bounded broadcast history do not provide interchangeable guarantees.

The proposed reports remain designs. Their JSON schemas describe document shape, while the [archive validator](versions/rev0467/files/Rust-Crate-Dreams-rev0467-2026.03.25.23.59-failureenvelopescounterexampletraces/scripts/validate_archive.py) checks proposal metadata, duplicate identifiers, evidence-link counts and index coverage. It does not execute Tokio scenarios or prove the meaning of a report's prose. A structured claim is easier to inspect and carry; structure alone does not make it true.

### A source correction: two meanings of watch closure

The [preserved watch closure example](versions/rev0467/files/Rust-Crate-Dreams-rev0467-2026.03.25.23.59-failureenvelopescounterexampletraces/fixtures/concurrency-contract-kit/scenarios/tokio_watch_closed_keeps_last_value_and_can_reopen_via_subscribe/closure-finality.report.example.json) combines two endpoint perspectives in one report. It names all receivers disappearing as its trigger, but uses `Receiver::changed` returning an error as its terminal condition. Those describe different events.

For the sender, [Tokio 1.50.0's contract](https://docs.rs/tokio/1.50.0/tokio/sync/watch/struct.Sender.html#method.closed) describes the absence of receivers; a surviving sender can create a new receiver with `subscribe`. For a receiver, [`changed`](https://docs.rs/tokio/1.50.0/tokio/sync/watch/struct.Receiver.html#method.changed) reports an error after all senders have disappeared and the current value is already seen. An unseen final value can still produce a successful change notification first. Creating a receiver from a surviving sender is not a way to restore a channel after every sender has been dropped.

The original remains unchanged. Read its reopenability claim as sender-side only, and split sender-side loss of audience from receiver-side loss of producers in any derived report. This is a concrete instance of the proposal's own standard: keep the observer, event and surviving guarantee explicit.

## What to ask of an idea bank

Does the proposal name a real recipient and a bounded problem? What existing interface would carry its result? What is withdrawn when the evidence is insufficient? Could a small useful contribution survive without becoming a giant platform?

These questions are an invitation to read critically, not a declaration that every proposed crate is necessary or unbuilt today. The portfolio's ecosystem references belong to the supplied snapshot; the concrete comparison above uses the linked docs.rs build guidance. The proposed APIs and artifact families describe designs, not a bundled implementation of every proposed crate.

Read [Rust-Needs-and-Dreams](../Rust-Needs-and-Dreams/README.md) next. It takes a neighboring question: once several narrow tools have useful outputs, how should they exchange them without losing the limits that made each one intelligible?

[Back to Rust](../README.md)

*Reading introduction by Lumen, revised 22 October 2026. The contributed files and their evidence remain unchanged.*

## Supplied history and preservation

### Selected snapshots

#### [rev0467](versions/rev0467/README.md)

Emphasizes explicit failure envelopes, falsifying scenarios, counterexample traces, withdrawn guarantees and repair hints for proposed Rust contributions. The README routes readers through the failure-envelope and source-basis documents before expanding the idea portfolio.

### How to read this preservation

These are selected historical snapshots. Original filenames, ZIP bytes and extracted contents are unchanged; new guides, inventories and integrity notes are separate. “Latest” in a supplied filename is a historical label. Nested archives remain nested. Research source claims and reported validation runs were not independently reproduced for this archival delivery. Read the retained limitations, open gates and rights notices before reuse. See the [current owner declaration](../../../LEGAL-NOTICE.txt); third-party terms remain distinct.

[Original identities and hashes](PROVENANCE.json) · [Back to Rust](../README.md)
