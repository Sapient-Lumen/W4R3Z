# Measurement plan page — question, baseline, and isolation contract interface spec

## Purpose

The archive already had throughput expectation and profiler capture review.
What it still lacked was one fixed page for another ordinary question:

> before we stop or quiet anything and run a benchmark, what exact performance question are we isolating, against which baseline, on which peer pair, and under what comparison contract?

A capacity-isolation experiment is not just `run iperf`.
It temporarily changes the system under observation and creates a comparison problem afterward.
AnonSync should therefore model it as a reviewed **measurement plan page** before any sidecar benchmark or performance knob change begins.

## Core decision

Every serious performance experiment must preserve four truths before execution:

1. the question being tested
2. the live baseline observation being compared against
3. the quiescence / isolation contract
4. the criteria for what result would justify a later tuning change

## Fixed review order

1. **Question to isolate**
2. **Baseline Sync observation**
3. **Scope and witness pair**
4. **Isolation / quiescence contract**
5. **Measurement matrix**
6. **Comparison and decision rules**

## 1) Question to isolate

The page should force the operator to choose the question class, for example:

- `raw network ceiling between these peers`
- `route-class penalty versus direct path`
- `upload asymmetry between source and receiver`
- `Sync-overhead suspicion after network ceiling established`
- `security/filter or disk-path suspicion`

The page must not let several materially different questions blur into one benchmark run.

## 2) Baseline Sync observation

Show the live symptom being compared against:

- affected transfer or share
- observation window
- observed upload / download band
- route class during the symptom
- workload shape summary
- current disk / internal-task context if known

The operator must be able to answer:

> what live Sync behavior are we trying to explain with this experiment?

## 3) Scope and witness pair

Show:

- benchmark participants
- current listening / route identity as relevant
- whether this is a pairwise experiment or a representative pair for a larger incident
- whether reverse-direction testing is required
- any missing witness or environment note that weakens generalization

## 4) Isolation / quiescence contract

The page must explicitly classify what must be made quiet first:

- `Sync fully shut down`
- `only this share quieted`
- `background hashing / indexing still present`
- `OS/network still shared with other traffic`
- `cannot isolate honestly on this host right now`

The page may not allow an external benchmark to look authoritative if live Sync or another confounder is still materially consuming the same path.

## 5) Measurement matrix

Show the planned subtests, such as:

- forward TCP
- reverse TCP
- forward UDP at target band
- reverse UDP at target band

But the page should treat them as reviewed measurement rows, not just pasted commands.
Each row should include:

- transport family
- direction
- target peer pair
- port / endpoint basis
- bandwidth target if applicable
- expected diagnostic value
- stop condition if the row becomes invalid

## 6) Comparison and decision rules

Before the run starts, publish what later verdicts mean, for example:

- `network ceiling well above observed Sync band -> investigate Sync/workload/disk/route overhead next`
- `network ceiling near observed Sync band -> network/path is likely dominant`
- `results diverge sharply by direction -> asymmetry remains in play`
- `results invalid because quiescence contract failed -> do not promote to tuning`

## Compact rendering obligations

Any compact card for a pending experiment must still preserve:

- question class
- baseline observation band
- pair / direction scope
- required quiescence level
- strongest allowed next conclusion

## Anti-clone rule

Do not clone workflows that drop the operator straight into terminal commands or tuning folklore.
AnonSync should not allow a sidecar benchmark unless the reviewed page already says what the benchmark is for, what had to become quiet, and how the result will be interpreted back in product terms.
