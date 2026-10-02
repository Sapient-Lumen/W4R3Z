# ADR 0332: Qualify one whole-VMM tree-v2 workspace cut

- Status: accepted, implemented, and corrected Sandwurm qualification passed
- Date: 2026-09-04

## Context

ADR 0325 killed one Agent during a signed tree-v2 workspace exchange, then restarted that process
on the still-running kernel and mounted filesystems. That is useful process-crash evidence, but it
does not exercise loss of the complete VM, the outer root filesystem's journal replay, disappearance
of every guest process, or a second kernel boot from the exact cut disk.

A credible power-cut gate also cannot accept a merely converged result. It must inspect the durable
projection before starting the recovering Agents and reject any state other than the exact prior
tree or exact completed tree. The host must prove which VMM it killed, and the recovery run must
prove it booted a copy of that VMM's exact writable disk rather than a clean image.

## Decision

Add a two-epoch, source-linked Sandwurm qualification for one tree-v2 workspace-exchange boundary:

1. The first networkless 2-vCPU/2-GiB KVM guest creates three separate loop-backed ext4 node roots,
   forms a three-writer mesh, and converges a durable 17-file baseline.
2. Writer C stops while A and B converge a 32-MiB successor. The guest fsyncs a content-free marker
   containing the exact prior/successor summaries and hashes of all node identities before C starts.
3. C starts. Only after its signed workspace journal's raw phase byte is exactly 2
   (`pending-exchange`) does the guest publish a content-free arm receipt through the Sandwurm
   workspace. A projection-stage observation is valid only while that same byte remains 2. The arm
   carries both the raw byte and the explicit `stable=1,pending-exchange=2` encoding. It performs no
   explicit root-disk flush after that observation.
4. The host locates exactly one descendant Cloud Hypervisor whose argv names the task-owned writable
   runtime disk. It records PID, Linux process start time, and argv SHA-256, then sends `SIGKILL` to
   that VMM only. The verifier binds these values to Sandwurm's terminal launch receipt and requires
   nonzero VMM exit with no `ch-remote` shutdown.
5. The second epoch evaluates the same committed guest closure and uses Sandwurm's root-image
   preseed path to reflink or copy the exact crash disk into a new task-owned writable runtime disk.
   Its runtime-root receipt must name epoch one's disk as its source. A different kernel boot ID is
   mandatory.
6. After outer and inner ext4 journal replay, but before any Agent starts, A and B must expose the
   completed tree and C may expose only the exact prior or completed tree. Any hybrid, malformed
   workspace header, conflict projection, or changed node identity fails closed. Normal startup must
   then converge all nodes to the successor, retain three branches per node, and pass repair.

The local DHT bootstrap used only for guest-internal rendezvous is deliberately boot-scoped. The
first diagnostic run showed why: its own key file was zero-length after the VMM cut, so treating that
ephemeral helper as durable state prevented recovery from reaching IoTox. Node identities and all
state under test remain on the reused crash image; only the unrelated bootstrap rendezvous is fresh.

`iotox-sandwurm-lab.sh` exposes `up-sync-power-cut`, `verify-sync-power-cut`, and
`export-sync-power-cut`. The exporter retains only ten JSON records plus a strict digest manifest;
disk images, node state, keys, content, and console logs stay out of the compact proof.

## Consequences

The first source-linked run, `wjlem1i2` at commit
`2cd84a29e2ae78e5f9b8ef5dc30af713116340a9`, crossed a real VMM reboot and passed its offline-tree,
identity, convergence, branch, and repair checks. A later source audit found that the Python observer
mapped byte 1 to `pending` and byte 2 to `stable`, exactly opposite the C++ enum and signed codec.
It therefore armed on a stable journal. The workspace-exchange claim, the v1 verifier acceptance,
and compact-proof qualification are withdrawn.

The corrected v2 schemas require phase byte 2 and carry the explicit phase encoding through every
proof layer. The regression self-test decodes byte 1 as stable, byte 2 as pending, and rejects an
unknown value; the host arm validator rejects byte 1. Existing v1 proof cannot pass the v2 verifier.

Corrected source-linked run `4hto8rll` at commit
`3dcc675a3be41ed8620021762bedc359bbff7d21` observed and proof-bound raw phase byte 2 before the
host cut. The exact crash lineage booted under a distinct second kernel with offline views
`[completed, completed, prior]`; C retained pending byte 2 and no stage path. All identities were
preserved, and the Agents converged and repaired three branches per node to 18 files, one directory,
33,619,995 bytes, and tree digest
`e1c1515d0faf3e669849a3913cd0fcb3faddb689ae911eedf2d9cee9e6e9bd2d` in 1.973 seconds. The first
VMM exited 137 without cooperative control, epoch two exited normally, and the complete campaign
took 435.628 seconds.

Compact proof `.sandwurm/exports/sync-power-cut/run.4hto8rll` independently verifies. Its manifest
SHA-256 is `33b5ae2a0c1bec039059292db0519550f36fcccf49d275caf052dc1cc5520128`.

This closes one corrected whole-VMM workspace linearization. One run does not cover every named
transaction boundary, repeated/random cuts,
near-ceiling or long-soak cuts, host reset or physical power removal, controller-cache semantics,
lying storage, torn writes below the virtual block layer, flash behavior, backup independence, or
precious-data approval. Those remain explicit graduation gates.
