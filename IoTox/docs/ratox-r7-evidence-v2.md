# Ratox R7 v2 evidence construction

This document is the operator contract for constructing, co-signing, sealing, and analyzing one
Ratox R7 complete-service run. ADRs 0069, 0070, and 0071 define the normative measurement and evidence
boundaries.

A successful command sequence creates a cryptographically bound evidence set. It does not by itself
prove that a route was direct UDP, that TCP-only containment was effective, that two physical hosts
were used, or that the capture binaries were uncompromised. Preserve the raw files and review them.

## 1. Create one balanced schedule

Generate a public run ID and seed once on the experiment coordinator:

```sh
run_id=$(python3 -c 'import secrets; print(secrets.token_hex(16))')
seed=$(python3 -c 'import secrets; print(secrets.token_hex(32))')
python3 tools/prepare-ratox-r7.py schedule \
  --run-id "$run_id" \
  --seed "$seed" \
  --samples-per-cell 1000 \
  --output schedule.tsv
```

The canonical schedule has 12,000 trials by default. Every contiguous twelve-trial block contains the
full two-route by six-load matrix exactly once, in a deterministic pseudorandom permutation. The
counter stream is domain-separated and bound to both run ID and seed, so reusing a seed for a new run
does not recreate the old order. Do not edit the file. A different sample count must remain within
1,000..10,000 per cell.

## 2. Create one ephemeral capture key on each host

Run the controller command on the controller and the host command on the terminal host. The secret
files are binary 64-byte Ed25519 keys and must remain mode 0600.

```sh
python3 tools/prepare-ratox-r7.py keygen \
  --secret-key controller-capture.key \
  --public-key controller-capture.pub

python3 tools/prepare-ratox-r7.py keygen \
  --secret-key host-capture.key \
  --public-key host-capture.pub
```

Retain the public keys with the run. Destroy the ephemeral secret keys after the final sealed bundle
and independent copies have been verified, according to the experiment's retention policy. Do not
reuse stable IoTox authority, owner, recovery, or device-identity keys.

Record each running Linux kernel identifier on its own machine:

```sh
cat /proc/sys/kernel/random/boot_id
```

The IDs must be distinct. A signing command later refuses a payload whose role-specific boot ID does
not match the machine currently performing the signature.

## 3. Execute the schedule and retain raw observations

Run trials in exact schedule order. Keep one nonempty route-observation file and one nonempty
bulk-load-observation file. They must be different regular files with different byte content. These
may be packet-capture summaries, network-namespace/firewall state,
load-generator output, process telemetry, or another format defined by the experiment procedure. The
constructor hashes their exact bytes; the analyzer requires the same files again.

The measurement file begins with two sorted metadata records:

```text
run-id<TAB>32-lowercase-hex
schema<TAB>iotox-ratox-r7-measurements-v1
```

Each following row has exactly 22 tab-separated fields:

```text
measurement
ordinal
token
controller_input_us
controller_output_us
controller_render_us
host_receive_us
host_input_commit_us
host_output_us
owner_queue_wait_us
input_commits
render_copies
complete
session_id
input_message_id
input_sequence
input_next_sequence
output_sequence
output_next_sequence
host_stage_event_ordinal
host_commit_event_ordinal
host_output_event_ordinal
```

The first word is literal `measurement`; the remaining fields occupy the same line. Timestamps and
owner queue wait are integer microseconds. Controller timestamps must come from one steady clock and
host timestamps from one host steady clock. Never subtract, add, order, or otherwise combine values
across those clock domains. The
controller interval is input admission through render completion. Host journal coordinates join the
exact INPUT admission, whole-frame PTY commit, and OUTPUT append without retaining terminal content.

One R7 keypress row must identify exactly one input byte:

```text
input_next_sequence = input_sequence + 1
```

The output span must be nonempty. Host event ordinals must be globally increasing and unique. Input
message IDs and input/output spans must not be reused or overlap within a session. Every row must
report one input commit, one render copy, and completion.

The construction capture client is `tools/ratox-terminal-probe.py`. It speaks the frozen private
`terminal.sock` protocol to the production controller, sends only one byte at a time, requires the
remote PTY to return that exact byte, copies the returned byte through a local pseudoterminal, and
timestamps completion only after the copy is observed at the pseudoterminal master. It deliberately
waits for the controller's interactive owner-command counter after INPUT and before OUTPUT_ACK. The
delta of the separately published cumulative queue-wait total is therefore the exact INPUT owner
queue wait; another interactive command in that interval invalidates the trial. Its raw output is a
capture input, not a sealed R7 bundle and not a qualification result by itself.

## 4. Construct the canonical unsigned bundle

Use the exact source commit that produced the tested binaries:

```sh
source_commit=$(git rev-parse HEAD)
python3 tools/prepare-ratox-r7.py prepare \
  --schedule schedule.tsv \
  --measurements measurements.tsv \
  --source-commit "$source_commit" \
  --controller-boot-id "$controller_boot_id" \
  --host-boot-id "$host_boot_id" \
  --controller-public-key controller-capture.pub \
  --host-public-key host-capture.pub \
  --route-evidence route-evidence.bin \
  --bulk-evidence bulk-evidence.bin \
  --output evidence.unsigned.tsv
```

Construction reparses the deterministic schedule, requires an exact row-for-trial match, validates all
same-clock timestamp and span invariants, derives canonical sample rows, and binds exact sizes plus
SHA-256 digests of the schedule, samples, route evidence, and bulk evidence. Metadata records two
capture roles and distinct kernel boots, while physical topology, route topology, and bulk-load
semantics remain explicitly marked `external-review-required`.

## 5. Create and sign role-specific payloads

Create both canonical payloads on the coordinator:

```sh
python3 tools/prepare-ratox-r7.py attestation-payload \
  evidence.unsigned.tsv --role controller --output controller.payload
python3 tools/prepare-ratox-r7.py attestation-payload \
  evidence.unsigned.tsv --role host --output host.payload
```

Transfer each payload to its corresponding capture machine without altering bytes. Sign on that
machine with its own ephemeral secret key:

```sh
python3 tools/prepare-ratox-r7.py sign controller.payload \
  --secret-key controller-capture.key \
  --output controller.signature

python3 tools/prepare-ratox-r7.py sign host.payload \
  --secret-key host-capture.key \
  --output host.signature
```

Signing verifies canonical payload shape, the local kernel boot ID, secret-key consistency, and the
bound public key before creating a detached signature.

## 6. Seal and independently analyze

Return the signatures to the coordinator and seal the exact unsigned bundle:

```sh
python3 tools/prepare-ratox-r7.py seal evidence.unsigned.tsv \
  --controller-signature controller.signature \
  --host-signature host.signature \
  --output evidence.sealed.tsv
```

The sealer verifies both signatures and reparses the exact final bytes. Analyze only with the bound
external files present:

```sh
python3 tools/analyze-ratox-r7.py evidence.sealed.tsv \
  --route-evidence route-evidence.bin \
  --bulk-evidence bulk-evidence.bin \
  --json-report report.json
```

Exit status 0 means every required cell satisfies the numeric and semantic R7 gates. Status 1 means a
well-formed, correctly signed run failed one or more qualification thresholds. Status 2 means the
bundle or an auxiliary input was invalid and no qualification result exists.

The deterministic text and JSON reports include p50/p95/p99 for controller end-to-end, host
receive-to-PTY, host PTY-to-output, controller output-to-render, and owner queue wait independently.
These stage distributions are diagnostic; they are never summed across hosts.

## 7. Retention and review checklist

Retain the sealed evidence, schedule, raw measurements, exact route and bulk evidence, deterministic
text/JSON reports, tested source commit or repository datacube, binary hashes, host inventory, kernel
and toolchain identity, experiment procedure, and operator/reviewer notes. Review the route and load
files semantically; the analyzer binds their bytes but does not infer network topology or load truth.

Treat a PASS as an evidence-gate result, not a production-readiness verdict. Physical qualification
also requires independent review of setup, capture quality, route containment, clocks, resource
telemetry, and non-latency R7 requirements.
