# Resilio instrumentation-posture mutation, restart truth, and baseline-return evaluation

## Why this seam matters

Another current official Resilio pass exposes a tighter non-clone reason than `collect the right artifacts` or `package them clearly`.
Current official docs are also candid that **evidence often requires changing the product's own operating posture first**:

- the current `Collecting debug logs automatically` guide still says to enable debug logging in settings or via a hidden `debug.txt` file containing `FFFFFFFF`, then restart Sync to make sure logging is enabled, then reproduce the issue and collect at least 15 minutes of logs
- the current `Collecting debug logs manually` guide still repeats the same enable-and-restart ritual and still says operators with many files should consider increasing log size after turning debug logging on
- the current `Increasing Debug Log size` guide still says default rotation is `100 Mbytes`, still says `sync.log` is backed up to `sync.log.old`, still says operators should raise `log_size` to `200` or more and restart, and for older Linux/NAS versions still falls back to editing `settings.dat` with a Python script after shutting Sync down without `kill -9`
- the current `Power user preferences` article still lists `log_size 100 (MB)`, `log_ttl 7 (day)`, and `profiler_enabled false`, and still says `profiler_enabled` writes `profiler.dat`, rotates it every 10 minutes, and requires client restart to activate
- the current `Resilio Sync 3.0 change log` still shows the live v3 line through `3.1.2.1076`

That candor is useful.
Resilio is not pretending that deeper capture is free, immediate, or identical to the default runtime.

The non-clone problem is still **instrumentation-posture ownership**.
One ordinary operator answer is still reconstructed from support prose, power-user settings, hidden files, restarts, and memory:

> what temporary diagnostic posture is active right now, how does it differ from baseline, what restart or dwell debt is still outstanding, what cost or residue does it introduce, and has the product actually returned to normal afterward?

## What current official docs still get right

### 1) Diagnostic capture is a posture change, not just a send action

Current docs still admit that:

- enabling debug logging changes runtime behavior before any packet exists
- `profiler_enabled` is a separate capture family with its own artifact (`profiler.dat`) and restart requirement
- log-size changes affect retention and rotation shape, not just export size
- some capture-enabling routes live in advanced/power-user settings or hidden storage paths rather than ordinary UI

That is better than pretending `include logs` is the whole story.

### 2) Restart and dwell truth really matter

Current docs still say:

- restart is needed to ensure debug logging is enabled
- profiler capture requires restart to activate
- at least 15 minutes of post-reproduction logging is desirable for enough information
- larger log buffers can be necessary when issue volume would rotate evidence away

So the live posture really does have pending conditions and sufficiency thresholds.

### 3) Retention and residue are real consequences

Current docs still imply or state that:

- debug logs persist with rotation and TTL behavior
- profiler traces rotate every 10 minutes
- larger `log_size` means larger on-disk diagnostic residue
- some changes are asymmetrical across platforms, because mobile platforms cannot adjust log size while desktop and older Linux/NAS paths can

So the cost of capture is not only cognitive; it is operational and local.

## Where the current contract still fails

### 1) Baseline versus temporary diagnostic posture is still not one object

Current docs still do not leave one product-owned record saying:

- what the previous baseline setting values were
- what exact diagnostic deltas are active now
- which deltas are pending restart versus already effective
- who asked for the deltas and for which incident question

So operators improvise with memory and screenshots.

### 2) Hidden and advanced enablement routes still leak policy

The current guides still require or allow several activation routes:

- ordinary settings toggles
- hidden tray/system-tray affordances
- `debug.txt` with `FFFFFFFF`
- power-user setting edits
- direct `settings.dat` surgery for older Linux/NAS versions

Yet there is still no first-class review surface saying which route won, what policy level it belongs to, and what stronger sentence about supportability is still forbidden.

### 3) Restoration to baseline is still folklore

The current docs still focus on capture and send, not on one reviewed restore object that says:

- whether the diagnostic posture should now be turned off
- whether larger `log_size` should return to its prior value
- whether profiler capture is still armed accidentally
- what diagnostic residue remains even after settings return to baseline

So `we collected enough` and `the product is back to normal` are still dangerously easy to conflate.

### 4) Later receipts can overstate certainty

Even after evidence is exported, the operator still lacks one durable receipt that says:

- what temporary posture was active during the capture window
- which deltas were never actually activated because restart never happened
- whether retention/rotation could still have clipped evidence
- whether the system has or has not yet been restored to its prior baseline

## What AnonSync should do instead

AnonSync should keep the candor and reject hidden posture folklore.
The product should own four ordinary page families for this seam:

1. **Instrumentation plan page**
   - diagnostic question
   - baseline posture
   - proposed deltas
   - cost/retention budget

2. **Instrumentation change review page**
   - exact setting/value or hidden-route delta
   - activation route and authority
   - restart gate and dwell expectations
   - side-effect scope and forbidden overclaims

3. **Instrumentation restore review page**
   - return-to-baseline plan
   - active residue and retained artifacts
   - what remains intentionally left on
   - cleanup and reopen boundary

4. **Instrumentation posture receipt page**
   - baseline at start
   - active deltas during capture
   - restart/activation truth
   - restoration state and claim ceiling

## Sharper non-clone line

So the tighter conclusion for this pass is:

> Resilio is still worth borrowing for its candor that evidence collection often requires temporary runtime posture changes, restarts, bigger retention buffers, and separate profiler capture. But it is not worth cloning the way the operator still has to remember those deltas from support prose, power-user settings, hidden files, and restart ritual instead of reading one durable instrumentation object with baseline, active delta, and restoration truth.

## New replacement pages added in this revision

- `772` Instrumentation plan page
- `773` Instrumentation change review page
- `774` Instrumentation restore review page
- `775` Instrumentation posture receipt page
