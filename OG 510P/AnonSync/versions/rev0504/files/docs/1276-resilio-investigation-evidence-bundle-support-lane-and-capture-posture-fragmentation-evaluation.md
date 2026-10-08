# Resilio investigation-evidence bundle, support lane, and capture-posture fragmentation evaluation

## What current official docs still make clear

Another current Resilio pass strengthens the archive's clone-veto line rather than weakening it.

Current official docs still say several things that are operationally real and worth borrowing:

- current `Collecting debug logs manually` and `Collecting debug logs automatically` docs still say debug logging must be enabled before reproduction, an alternate `debug.txt` trigger exists, and Sync should be restarted so the capture posture is real rather than only requested
- those same current docs still say operators should let Sync collect logs for at least 15 minutes after reproducing the issue, which means evidence window and symptom window are different truths
- current `Increasing Debug Log size` docs still say logs rotate at a configurable size and default rotation is finite, which means `logging enabled` is weaker than `the needed evidence survived`
- current `Collecting crash reports, mini-dumps and core dumps` docs still separate ordinary logs from crash reports, mini dumps, and explicit core dumps, and the artifact path changes if Sync runs as a service under a different account
- current `Where to collect logs on NAS?` docs still say NAS evidence locations vary by vendor and sometimes require consulting the config to find the real storage path
- current `Collect debug logs on mobiles` and `Settings on mobile platforms` docs still say mobile evidence has its own export path and cleanup can clear residual files together with current debug logs
- current `Measuring network performance with iperf3` docs still require Sync to be shut down completely during the benchmark, which means comparative transport evidence is different from in-situ runtime evidence
- those same current troubleshooting docs still say direct technical support is available only for Business customers, while Sync v3 otherwise routes functionality help toward the forum and Help Center

That is real candor.
It is useful product truth.

## What still should not be cloned

The operator is still asked to reconstruct one practical answer to:

> what evidence can I capture right now, what lane can actually receive it, what survives rotation or cleanup, and what stronger diagnostic sentence remains unproven?

Current Resilio docs still scatter that answer across manual-log, automatic-log, crash-dump, NAS-path, mobile-settings, and iperf articles.

That means several materially different questions remain merged unless the operator does their own synthesis:

1. **am I in a direct-support lane, a self-serve lane, or only a community-help lane?**
2. **is the product currently in a capture posture that can observe the issue, or did I only request logging without restart or enough runtime?**
3. **what artifact class am I actually collecting: rolling logs, feedback bundle, crash dump, core dump, or external benchmark?**
4. **what evidence survives log rotation, cleanup, service-account storage differences, or vendor-specific NAS paths?**
5. **did this evidence come from live runtime, post-crash residue, or an offline comparative test with Sync stopped?**

That page-contract gap is exactly why AnonSync should not clone the behavior.

## Why this matters for AnonSync

AnonSync should borrow six habits directly:

- **say openly when support lane and evidence lane are different truths**
- **say openly when logging was requested but not yet proven active**
- **say openly when evidence requires a reproduction window rather than instant capture**
- **say openly when logs, crash dumps, core dumps, and external benchmarks are different artifact classes**
- **say openly when cleanup or rotation can erase future diagnostic power**
- **say openly when a benchmark requires runtime shutdown and therefore cannot prove live in-process behavior**

But AnonSync should reject six weaker habits:

- one generic `send logs` action that hides the actual support lane
- one generic `debug enabled` sentence that hides restart, window length, and artifact survival
- one generic `diagnostic bundle` label that collapses logs, dumps, and offline benchmarks
- silent rotation or cleanup that launders away evidence survivorship
- service-account or NAS-path differences hidden behind one fake storage location
- escalation UI that implies direct human support when the lane is actually self-serve or community-only

## Replacement pages added for this seam

This revision therefore adds six narrower replacement pages:

- `1277` — Investigation-evidence contract sheet
- `1278` — Evidence-capture review
- `1279` — Support-lane proof
- `1280` — Evidence-retention timeline
- `1281` — Investigation-evidence lineage receipt

These pages keep the Resilio candor and reject the scattered-supportability contract.

## Sharper non-clone line after this pass

The archive now has one tighter sentence for this seam:

> borrow Resilio's candor that support entitlement, live log capture, rotated-log survival, crash residue, mobile export, NAS storage paths, and offline iperf benchmarking are different truths; refuse any interface contract where `what evidence can I capture now, who can actually receive it, and what diagnostic claim does it justify?` still makes the operator merge half a dozen troubleshooting articles instead of one explicit investigation-evidence object.
