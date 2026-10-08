# Resilio sidecar-benchmark ritual, capacity isolation, and tuning folklore evaluation

## Purpose

The archive already had performance visibility, throughput expectation, route proof, disk-pressure explanation, and profiler capture review.
What it still lacked was one explicit comparison document for another ordinary seam:

> when the operator says `is the network actually the limiter here, or is Sync/workload/disk the limiter?`, where does the product itself own the controlled measurement, the quiescence contract, and the safe comparison back to live transfer behavior?

Current official Resilio docs are good enough that AnonSync needs a serious answer.
Resilio is not unserious about speed.
It names relay penalties, many-small-file penalties, asymmetrical upload peers, security-software delay, disk-priority effects, and direct-versus-relayed route quality.
It also publishes an iperf3 guide that openly says Sync should be shut down completely on both peers during the test.
That honesty is worth preserving.

## What Resilio gets right

Resilio is still right that:

- `slow` is not one cause
- directness, LAN locality, and known hosts can materially change results
- some speed questions need a measurement that isolates the raw peer-to-peer network from Sync's own file, hash, queue, and disk work
- performance experiments should run in both directions, not just one optimistic path
- knob changes like disabling LAN encryption or low-priority disk mode are not magic; they are hypotheses about a bottleneck family

This is better than products that hide all performance truth behind one spinner and one vague `network issue` line.

## What still should not be cloned

The measurement contract is still scattered and too support-shaped.
Current official Resilio docs still require the operator to combine at least five article families:

1. **Slow-speed troubleshooting** for relay use, many-small-file workload, asymmetrical peers, security software, disk priority, and port/directness issues
2. **Speed-improvement guidance** for direct-path preference, same-LAN/VPN tactics, predefined hosts, rate limits, encryption, and disk priority
3. **Power-user preferences** for the real defaults and names of those performance-related controls
4. **Internal-task warnings** for the fact that hashing, merging, scanning, deduplication, and writing can consume disk/CPU independently of raw network capacity
5. **iperf3 instructions** for a fully external benchmark that requires Sync to be shut down completely on both peers while commands are run sequentially in terminal

That means one ordinary answer is still reconstructed from several places:

- what exact question are we isolating with this benchmark?
- which peers and directions are in scope?
- what had to be quiesced before the benchmark could mean anything?
- how should the external result be compared back to the observed Sync transfer?
- which later tuning changes are worth trying, and what semantic or security cost do they carry?

The substance is useful.
The workflow ownership is still weak.

## Why this matters for AnonSync

AnonSync should not repeat two common mistakes:

1. **benchmark folklore** — pasting external commands without a reviewed question, quiescence proof, or comparison target
2. **tuning folklore** — recommending directness, encryption, or priority changes without an explicit upside claim and side-effect review

A serious sync product needs one stable public answer to four different questions:

- **measurement truth** — what exactly are we trying to isolate?
- **quiescence truth** — what workload or runtime had to be paused or stopped first?
- **comparison truth** — what does the sidecar result say about the live Sync bottleneck, and what does it not say?
- **intervention truth** — which next configuration or route change is justified, reversible, and semantically acceptable?

## Replacement pages in this revision

This revision adds four fixed pages:

- `777` — Measurement plan
- `778` — Sidecar benchmark run
- `779` — Performance hypothesis review
- `780` — Measurement receipt

Together they replace article-shaped benchmarking and tuning lore with product-owned experimental reasoning.

## The doctrinal line

Borrow directly:

- the candor that direct versus relayed path matters
- the candor that file shape and hidden internal tasks can make Sync slower than raw network throughput
- the candor that some questions want a network-isolation benchmark outside the normal transfer path
- the candor that performance changes are hypotheses, not promises

Do not clone directly:

- support prose that makes the operator decide from memory what the benchmark was supposed to prove
- command snippets that are detached from a reviewed experiment object
- performance tuning suggestions that do not publish upside, policy cost, and revert plan
- later conclusions like `network is fine` or `Sync is the problem` that are not tied to preserved experiment conditions

## Conclusion

The correct AnonSync response is not merely `show more graphs` or `link to iperf`.
It is stronger than that:

> keep Resilio's candor that route class, workload shape, and raw network capacity are different things, but make every serious speed investigation compile into one reviewed experiment that states the isolation question, proves the quiescence contract, records the benchmark conditions, compares the result back to live Sync behavior, and only then proposes safe next changes.
