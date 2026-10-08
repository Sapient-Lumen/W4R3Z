# Proof obligations — rev0031

rev0031 obligations:

- Lease-bound probes must reject purpose mismatch, key crisis blocks, bad egress, replay, and low family diversity.
- Lease-bound probes must accept only when fresh lease, live probe, and egress agree.
- Repair debt must schedule hard-negative/tombstone work before bulk repair.
- Repair debt must reject expired, replayed, conflicting, and family-monocultured work.
- Repair debt must defer work by local budget without losing debt digests.
- Auditmesh must pass for the current rev0031 surface and preserve rev0030 keycrisisfold as predecessor.

Evidence:

- `tests/test_rev0031_leaseprobe_repairdebt_auditmesh.py`
- `scripts/ci/run_python_cloudtainer_lane.sh`
