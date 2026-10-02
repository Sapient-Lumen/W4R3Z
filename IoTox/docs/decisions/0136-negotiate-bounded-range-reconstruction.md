# ADR 0136: negotiate bounded range reconstruction

Status: accepted

Date: 2026-08-22

## Decision

IoTox adds optional `state-sync-ranges-v1` feature bit 26 above the existing
`state-sync-v1` service. Bit 26 is structurally invalid without bit 18. It allocates message type 24
for a bounded range request and type 25 for its correlated result. An Agent advertises both bits only
after the complete default-off synchronization publisher/subscriber and finite-file seams construct
successfully.

The subscriber may select the range path only when it has an authenticated accepted HEAD and the
exact digest-named artifact from that HEAD as a local basis. It first downloads, commits, and verifies
the candidate's complete range-v1 manifest. Planning is entirely local: the wire never carries basis
offsets, block matches, or a claimed reuse plan. The planner rehashes the immutable manifest and basis
under the namespace transaction, derives missing target-address-space ranges, and falls back to the
ordinary complete artifact request when there is no reusable basis, no reusable bytes, or the plan
exceeds the bounded request count.

A request carries 1..64 nonempty ranges. They are strictly increasing, nonoverlapping, nonadjacent,
and bound to the exact current signed-HEAD record and a nonzero request-selected Tox FileId. The
publisher rechecks current HEAD identity, publisher authority, artifact presence and digest, every
range bound, total byte quota, and retained replay before offering a file. The offered file is the
canonical concatenation of those ranges from one descriptor-pinned, mutation-checked artifact. It
does not materialize a server-side bundle file.

Before resuming the incoming bundle, the subscriber durably records the target artifact attempt and
uses its exact attempt-derived private staging path. On terminal completion it validates the private
file shape and exact concatenated size, unlinks its pathname while retaining the open descriptor,
and feeds missing target ranges from that descriptor into toxsync reconstruction. Reconstruction
revalidates the plan, manifest, and basis, writes only the attempt-derived output, and verifies the
complete target SHA-256. Only then may IoTox commit the artifact, clear the durable attempt, mark the
scheduler object committed, and accept the signed HEAD last. Activation remains a separate exact-
token local operation.

## Consequences

- A small successor edit can transfer fewer bytes without introducing a second trust root, a remote
  plan, pathname authority, or partial-object authority.
- One request and one Tox transfer carry all missing ranges. This is bounded delta transfer, not
  multi-route striping, provider-level sparse transfer, or restart-resumable c-toxcore state.
- The range path fails closed on a corrupt or missing basis. ADR 0137 permits only a fresh ordinary
  whole-successor request after the candidate manifest is independently verified; complete-object
  verification and accepted-HEAD-last ordering remain unchanged.
- Cancellation, disconnect, malformed terminal truth, reconstruction failure, and destruction keep
  or clear the signed attempt journal according to exact staging-cleanup truth. Cleanup failure cannot
  erase the durable recovery record.
- `sync-status` reports range negotiation, publisher range requests/offers/bytes, and per-pull range
  count, reused bytes, and fetched bytes without exposing content.
- Deterministic directories, partial-range restart/disconnect continuation, corrupt-object scrub,
  storage fault injection, multi-source scheduling, and destructive GC remain separate gates.

## Evidence

The owned test registry has 519 passing checks. New focused checks freeze the range codecs and
feature dependency, zero-copy canonical range file view, publisher authority/replay/bounds,
manifest-first subscriber reconstruction, exact SHA-256 commit, corrupt-source cleanup, corrupt-basis
refusal, malformed-plan refusal, and durable attempt clearance.

The live Agent/mock-toxcore test starts from an accepted generation-1 16 KiB basis and receives a
signed generation-2 successor through the real confirmed-session, v3 authority, lossless-control,
paused-file-offer, terminal-worker, and local-control path. It fetches one 4,096-byte contiguous
range, reuses 12,288 bytes, reconstructs the byte-exact target, and advances the accepted HEAD to
generation 2. The ordinary generation-1 whole-object Agent test remains passing. All runnable GCC
Debug process/restart gates pass on the founding host; five delegated-cgroup cases skip because this
host run did not supply a delegated cgroup root.

The genuine Sandwurm `sync-file-range` gate subsequently passed over direct UDP and forced TCP. Each
cell first activated a complete deterministic 4 MiB generation 1, then negotiated one range for a
parent-linked generation 2, fetched 128 bytes, reused 4,194,176 verified bytes, reconstructed the
exact successor, accepted its signed HEAD last, and explicitly activated that token. Both compact
proof exports independently reverify. Exact identities and nonclaims are retained in
`../evidence/2026-08-22-sandwurm-sync-range.md`.
